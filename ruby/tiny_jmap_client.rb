require "json"
require "net/http"
require "net/https"

class TinyJMAPClient
  attr_reader :username, :hostname, :token
  def initialize(hostname, username, token)
    if hostname.nil? || username.nil? || token.nil? || hostname.empty? || username.empty? || token.empty?
      raise ArgumentError("hostname, username, and token must be supplied as non nil, non empty strings")
    end

    @hostname = hostname
    @username = username
    @token = token
  end

  def session
    @session ||= fetch_session("https://#{@hostname}/.well-known/jmap")
  end

  def api_url
    session["apiUrl"]
  end

  def account_id
    # Return the accountId for the account matching self.username
    @account_id ||= session["primaryAccounts"]["urn:ietf:params:jmap:mail"]
  end

  def identity_res
    @identity_res ||= jmap_call([["Identity/get", {accountId: account_id}, "i"]], ["urn:ietf:params:jmap:submission"])
  end

  def all_identity_ids
    identity_res["methodResponses"][0][1]["list"].map { |user| {email: user["email"], id: user["id"]} }
  end

  def identity_id(email = nil)
    # Return the identityId for an address matching @username or email if supplied
    if email.nil?
      email = @username
    end
    acct = identity_res["methodResponses"][0][1]["list"].select { |user| user["email"].downcase == email.downcase }
    if acct.any?
      acct[0]["id"]
    end
  end

  def jmap_call(method_calls, using = [])
    if !using.include?("urn:ietf:params:jmap:core")
      using.unshift("urn:ietf:params:jmap:core")
    end
    uri = URI(api_url)
    http = Net::HTTP.new(uri.host, uri.port)
    http.use_ssl = true
    http.verify_mode = OpenSSL::SSL::VERIFY_PEER
    body = JSON.dump({using: using, methodCalls: method_calls})
    req = Net::HTTP::Post.new(uri)
    req.add_field "Authorization", "Bearer #{@token}"
    req.add_field "Content-Type", "application/json"
    req.body = body
    resp = http.request(req)
    JSON.parse(resp.body)
  rescue => e
    puts "#{e.class}: #{e.message}"
    if defined?(resp)
      puts "Response code: #{resp.code}"
      puts resp.body
    end
  end

  private

  def fetch_session(uri_str, limit = 10)
    # This was extracted to its own method because net:http doesn't have a built in mechanism for handling redirects
    # There are more user friendly http clients for Ruby, but I am using net:http to minimize external dependencies
    if limit < 1
      raise StandardError.new("Too many redirects")
    end
    uri = URI(uri_str)
    http = Net::HTTP.new(uri.host, uri.port)
    http.use_ssl = true
    http.verify_mode = OpenSSL::SSL::VERIFY_PEER
    req = Net::HTTP::Get.new(uri)
    req.add_field "Authorization", "Bearer #{@token}"
    req.add_field "Content-Type", "application/json"
    resp = http.request(req)
    if resp["location"]
      fetch_session(resp["location"], limit - 1)
    elsif resp.code == "200"
      JSON.parse(resp.body)
    else
      raise StandardError.new(resp.msg)
    end
  end
end
