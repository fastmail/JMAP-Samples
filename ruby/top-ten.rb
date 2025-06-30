#!/usr/bin/env ruby

require "./tiny_jmap_client"

client = TinyJMAPClient.new(ENV["JMAP_HOSTNAME"] || "api.fastmail.com", ENV["JMAP_USERNAME"], ENV["JMAP_TOKEN"])
account_id = client.account_id

inbox_res = client.jmap_call(
  [["Mailbox/query", {accountId: account_id, filter: {role: "inbox", hasAnyRole: true}}, "a"]],
  ["urn:ietf:params:jmap:mail"]
)
inbox_id = inbox_res["methodResponses"][0][1]["ids"][0]

get_res = client.jmap_call(
  [
    [
      "Email/query",
      {
        accountId: account_id,
        filter: {inMailbox: inbox_id},
        sort: [{property: "receivedAt", isAscending: false}], limit: 10
      },
      "a"
    ],
    [
      "Email/get",
      {
        accountId: account_id,
        properties: ["id", "subject", "receivedAt"],
        "#ids": {resultOf: "a", name: "Email/query", path: "/ids/*"}
      },
      "b"
    ]
  ],
  ["urn:ietf:params:jmap:mail"]
)

get_res["methodResponses"][1][1]["list"].each { |email| puts "#{email["receivedAt"]} - #{email["subject"]}" }
