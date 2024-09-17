#!/usr/bin/env ruby

require "./tiny_jmap_client"

# Set up our client from the environment and set our account ID
client = TinyJMAPClient.new(ENV["JMAP_HOSTNAME"] || "api.fastmail.com", ENV["JMAP_USERNAME"], ENV["JMAP_TOKEN"])

account_id = client.account_id

# Here, we're going to find our drafts mailbox, by calling Mailbox/query
query_res = client.jmap_call(
  [["Mailbox/query", {accountId: account_id, filter: {name: "Drafts"}}, "a"]],
  ["urn:ietf:params:jmap:mail"]
)

# Pull out the id from the list response, and make sure we got it

draft_mailbox_id = query_res["methodResponses"][0][1]["ids"][0]

# Great! Now we're going to set up the data for the email we're going to send.
body = <<~EOF
  Hi!

  This email may not look like much, but I sent it with JMAP, a protocol
  designed to make it easier to manage email, contacts, calendars, and more of
  your digital life in general.

  Pretty cool, right?

  --
  This email sent from my next-generation email system at Fastmail.
EOF

draft = {
  from: [{email: client.username}],
  to: [{email: client.username}],
  subject: "Hello, world!",
  keywords: {"$draft": true},
  mailboxIds: {draft_mailbox_id => true},
  bodyValues: {body: {value: body, charset: "utf-8"}},
  textBody: [{partId: "body", type: "text/plain"}]
}

identity_id = client.identity_id

# Here, we make two calls in a single request. The first is an Email/set, to
# set our draft in our drafts folder, and the second is an
# EmailSubmission/set, to actually send the mail to ourselves. This requires
# an additional capability for submission.
method_calls = []
method_calls << ["Email/set", {accountId: account_id, create: {draft: draft}}, "a"]
method_calls << ["EmailSubmission/set",
  {
    accountId: account_id,
    onSuccessDestroyEmail: ["#sendIt"],
    create: {sendIt: {emailId: "#draft", identityId: identity_id}}
  },
  "b"]
create_res = client.jmap_call(method_calls, ["urn:ietf:params:jmap:mail", "urn:ietf:params:jmap:submission"])
puts(create_res)
