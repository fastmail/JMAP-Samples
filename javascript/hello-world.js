#!/usr/bin/env node
// bail if we don't have our ENV set:
if (!process.env.JMAP_USERNAME || !process.env.JMAP_TOKEN) {
  console.log("Please set your JMAP_USERNAME and JMAP_TOKEN");
  console.log(
    "JMAP_USERNAME=username JMAP_TOKEN=token node hello-world.js"
  );

  process.exit(1);
}

const hostname = process.env.JMAP_HOSTNAME || "api.fastmail.com";
const username = process.env.JMAP_USERNAME;

const auth_url = `https://${hostname}/.well-known/jmap`;
const Authorization = `Bearer ${process.env.JMAP_TOKEN}`;
const headers = {
  "Content-Type": "application/json",
  Authorization,
};

const getSession = async () => {
  const response = await fetch(auth_url, {
    method: "GET",
    headers,
  });
  return response.json();
};

const mailboxQuery = async (api_url, account_id) => {
  const response = await fetch(api_url, {
    method: "POST",
    headers,
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

const identityQuery = async (api_url, account_id) => {
  const response = await fetch(api_url, {
    method: "POST",
    headers,
    body: JSON.stringify({
      using: [
        "urn:ietf:params:jmap:core",
        "urn:ietf:params:jmap:mail",
        "urn:ietf:params:jmap:submission",
      ],
      methodCalls: [
        [
          "Identity/get",
          { accountId: account_id, ids: null },
          "a"
        ]
      ]
    })
  });
  const data = await response.json();

  return await data["methodResponses"][0][1]
    .list
    .filter(identity => identity.email === username)[0].id;
};

const draftResponse = async (api_url, account_id, draft_id, identity_id) => {
  const message_body =
    "Hi! \n\n" +
    "This email may not look like much, but I sent it with JMAP, a protocol \n" +
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
    headers,
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
            create: { sendIt: { emailId: "#draft", identityId: identity_id } },
          },
          "b"
        ]
      ]
    })
  });
  const data = await response.json();

  console.log(JSON.stringify(data, null, 2));
};

const run = async () => {
  const session = await getSession();
  const api_url = session.apiUrl;
  const account_id = session.primaryAccounts["urn:ietf:params:jmap:mail"];
  const draft_id = await mailboxQuery(api_url, account_id);
  const identity_id = await identityQuery(api_url, account_id);
  draftResponse(api_url, account_id, draft_id, identity_id);
};

run();
