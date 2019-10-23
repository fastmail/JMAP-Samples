#!/usr/bin/env lua

local tiny_jmap = require("tiny_jmap")

-- Set up our client from the environment and set our account ID
local client = tiny_jmap.new({
  hostname = os.getenv("JMAP_HOSTNAME") or "jmap.fastmail.com",
  username = os.getenv("JMAP_USERNAME"),
  password = os.getenv("JMAP_PASSWORD"),
})
local account_id = client:get_account_id()

-- Here, we're going to find our drafts mailbox, by calling Mailbox/query
local query_res = client:make_jmap_call(
  {
    using = {
      "urn:ietf:params:jmap:core",
      "urn:ietf:params:jmap:mail",
    },
    methodCalls = {
      {
        "Mailbox/query",
        {
          accountId = account_id,
          filter = {
            name = "Drafts",
          },
        },
        "a",
      },
    },
  }
)

-- Pull out the id from the list response, and make sure we got it
local draft_mailbox_id = query_res.methodResponses[1][2].ids[1]
assert(draft_mailbox_id)

-- Great! Now we're going to set up the data for the email we're going to send.
local body = [[
Hi!

This email may not look like much, but I sent it with JMAP, a new protocol
designed to make it easier to manage email, contacts, calendars, and more of
your digital life in general.

Pretty cool, right?

-- 
This email sent from my next-generation email system at Fastmail.
]]

local draft = {
  from = {{ email = client.username }},
  to = {{ email = client.username }},
  subject = "Hello, world!",
  keywords = {},
  mailboxIds = {},
  bodyValues = { body = { value = body, charset = "utf-8" } },
  textBody = {{ partId = "body", type = "text/plain" }},
}
draft.keywords["$draft"] = true
draft.mailboxIds[draft_mailbox_id] = true

-- Here, we make two calls in a single request. The first is an Email/set, to
-- set our draft in our drafts folder, and the second is an
-- EmailSubmission/set, to actually send the mail to ourselves. This requires
-- an additional capability for submission.
local create_res = client:make_jmap_call(
  {
    using = {
      "urn:ietf:params:jmap:core",
      "urn:ietf:params:jmap:mail",
      "urn:ietf:params:jmap:submission",
    },
    methodCalls = {
      {
        "Email/set",
        {
          accountId = account_id,
          create = {
            draft = draft,
          },
        },
        "a",
      },
      {
        "EmailSubmission/set",
        {
          accountId = account_id,
          onSuccessDestroyEmail = {"#sendIt"},
          create = { sendIt = { emailId = "#draft" }},
        },
        "b",
      },
    },
  }
)

local serpent = require("serpent")
print(serpent.block(create_res))
