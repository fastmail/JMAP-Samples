local request = require("http.request")
local cjson = require("cjson")

local tiny_jmap = {}

function tiny_jmap.new (args)
  local self = {}
  self.hostname = args.hostname
  self.username = args.username
  self.authorization = "Bearer "..args.token
  setmetatable(self, {__index = tiny_jmap})
  return self
end

function tiny_jmap:get_session ()
  if self.session then return self.session end

  local req = request.new_from_uri("https://"..self.hostname.."/.well-known/jmap")
  req.headers:append("Authorization", self.authorization)
  local headers, stream = assert(req:go())
  local body = assert(stream:get_body_as_string())
  if headers:get ":status" ~= "200" then
    error(body)
  end

  self.session = cjson.decode(body)
  return self.session
end

function tiny_jmap:get_account_id ()
  if self.account_id then return self.account_id end

  local session = self:get_session()

  self.account_id = session.primaryAccounts["urn:ietf:params:jmap:mail"]
  return self.account_id
end

function tiny_jmap:make_jmap_call (call)
  local session = self:get_session();

  local req = request.new_from_uri(session.apiUrl)
  req.headers:append("Authorization", self.authorization)
  req.headers:upsert("Content-Type", "application/json")
  req.headers:upsert(":method", "POST")
  req:set_body(cjson.encode(call))
  local headers, stream = assert(req:go())
  local body = assert(stream:get_body_as_string())
  if headers:get ":status" ~= "200" then
    error(body)
  end
  return cjson.decode(body)
end

return tiny_jmap
