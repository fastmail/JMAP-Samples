const fetch = require("node-fetch");

// bail if we don't have our ENV set:
if (!process.env.JMAP_USERNAME || !process.env.JMAP_PASSWORD) {
  console.log("Please set your JMAP_USERNAME and JMAP_PASSWORD");
  console.log(
    "JMAP_USERNAME=username JMAP_PASSWORD=password node hello-world.js"
  );

  process.exit(1);
}

const api_url = "https://betajmap.fastmail.com/api";
const auth_uri = "https://betajmap.fastmail.com/authenticate";
const username = process.env.JMAP_USERNAME;
const password = process.env.JMAP_PASSWORD;

const auth_token = Buffer.from(`${username}:${password}`).toString("base64");

const getAccountId = async () => {
  const response = await fetch(auth_uri, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: `basic ${auth_token}`
    }
  });
  const data = await response.json();

  return await data.primaryAccounts["urn:ietf:params:jmap:mail"];
};

const mailboxQuery = async account_id => {
  const response = await fetch(api_url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `basic ${auth_token}`
    },
    body: JSON.stringify({
      using: ["urn:ietf:params:jmap:core", "urn:ietf:params:jmap:mail"],
      methodCalls: [
        [
          "Mailbox/query",
          { accountId: account_id, filter: { name: "Drafts" } },
          "a"
        ]
      ]
    })
  });
  const data = await response.json();

  return await data["methodResponses"][0][1]["ids"][0];
};

const draftResponse = async (account_id, draft_id) => {
  const message_body =
    "Hi! \n\n" +
    "This email may not look like much, but I sent it with JMAP, a new protocol \n" +
    "designed to make it easier to manage email, contacts, calendars, and more of \n" +
    "your digital life in general. \n\n" +
    "Pretty cool, right? \n\n" +
    "-- \n" +
    "This email sent from my next-generation email system at Fastmail. \n";

  const draft_object = {
    from: [{ email: username }],
    to: [{ email: username }],
    subject: "Hello, world!",
    keywords: { $draft: true },
    mailboxIds: { [draft_id]: true },
    bodyValues: { body: { value: message_body, charset: "utf-8" } },
    textBody: [{ partId: "body", type: "text/plain" }]
  };

  const response = await fetch(api_url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `basic ${auth_token}`
    },
    body: JSON.stringify({
      using: [
        "urn:ietf:params:jmap:core",
        "urn:ietf:params:jmap:mail",
        "urn:ietf:params:jmap:submission"
      ],
      methodCalls: [
        [
          "Email/set",
          { accountId: account_id, create: { draft: draft_object } },
          "a"
        ],
        [
          "EmailSubmission/set",
          {
            accountId: account_id,
            onSuccessDestroyEmail: ["#sendIt"],
            create: { sendIt: { emailId: "#draft" } }
          },
          "b"
        ]
      ]
    })
  });
  const data = await response.json();

  console.log(JSON.stringify(data));
};

getAccountId().then(account_id => {
  mailboxQuery(account_id).then(draft_id => {
    draftResponse(account_id, draft_id);
  });
});
