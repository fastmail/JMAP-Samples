#!/usr/bin/env lua

local tiny_jmap = require("tiny_jmap")

local client = tiny_jmap.new({
  hostname = os.getenv("JMAP_HOSTNAME") or "jmap.fastmail.com",
  username = os.getenv("JMAP_USERNAME"),
  password = os.getenv("JMAP_PASSWORD"),
})

local account_id = client:get_account_id()

local inbox_res = client:make_jmap_call(
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
          filter = { role = "inbox", hasAnyRole = true },
        },
        "a",
      },
    },
  }
)
local inbox_id = inbox_res.methodResponses[1][2].ids[1]
assert(inbox_id)

local get_res = client:make_jmap_call(
  {
    using = {
      "urn:ietf:params:jmap:core",
      "urn:ietf:params:jmap:mail",
    },
    methodCalls = {
      {
        "Email/query",
        {
          accountId = account_id,
          filter = { inMailbox = inbox_id },
          sort = {
            {
              property = "receivedAt",
              isAscending = false,
            },
          },
          limit = 10,
        },
        "a",
      },
      {
        "Email/get",
        {
          accountId = account_id;
          properties = {"id", "subject", "receivedAt"};
          ["#ids"] = {
            resultOf = "a";
            name = "Email/query";
            path = "/ids/*";
          };
        };
        "b",
      },
    },
  }
)

for i,email in ipairs(get_res.methodResponses[2][2].list) do
  print(string.format("%s - %s", email.receivedAt, email.subject))
end
