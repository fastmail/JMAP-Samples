using JmapNet;
using JmapNet.Client;
using JmapNet.Models.Core;
using JmapNet.Models.Mail;

namespace JmapSamples;

internal static class Samples
{
    // query for the drafts mailbox, create a new email, and send it
    internal static async Task HelloWorld(this JmapClient jmap, string accountId, string userName)
    {
        // get drafts mailbox
        var mailboxQueryFilter = new JmapMailboxQueryFilter
        {
            Name = "Drafts"
        };

        var mailboxQueryRequest = new JmapMailboxQueryRequest(accountId)
        {
            Filter = mailboxQueryFilter
        }.Invoke("a");

        var mailboxQueryResponse = await jmap.SendRequest(mailboxQueryRequest);

        var draftMailboxId = mailboxQueryResponse
            ?.GetIds(mailboxQueryRequest)
            ?.SingleOrDefault() ?? throw new InvalidOperationException("couldn't get draft mailbox");

        // compose email
        const string emailBody =
            """
            Hi!
        
            This email may not look like much, but I sent it with JMAP, a protocol
            designed to make it easier to manage email, contacts, calendars, and more of
            your digital life in general.
        
            Pretty cool, right?
        
            -- 
            This email sent from my next-generation email system at Fastmail. 
            """;

        var email = new JmapEmail
        {
            From = new List<JmapEmailAddress> { new("", userName) },
            To = new List<JmapEmailAddress> { new("", userName) },
            Subject = "Hello, world!",
            Keywords = new Dictionary<string, bool> { { "$draft", true } },
            MailboxIds = new Dictionary<string, bool> { { draftMailboxId, true } },
            BodyStructure = new JmapEmailBodyPart { Type = "text/plain", PartId = "body" },
            BodyValues = new Dictionary<string, JmapEmailBodyValue> { { "body", new JmapEmailBodyValue { Value = emailBody } } }
        };

        // get identity
        var identityGetRequest = new JmapIdentityGetRequest(accountId).Invoke("i");
        var identityGetResponse = await jmap.SendRequest(identityGetRequest);
        var identities = identityGetResponse.GetItems<JmapIdentity>(identityGetRequest);
        var identity = identities.First(ident => ident.Email == userName);

        // chained Email/set and EmailSubmission/set calls in a single request
        var emailSet = new JmapEmailSetRequest(accountId)
        {
            Create = new Dictionary<string, JmapEmail> { { "draft", email } }
        }.Invoke("a");

        var emailSubmissionSet = new JmapEmailSubmissionSetRequest(accountId)
        {
            Create = new Dictionary<string, JmapEmailSubmission>
            {
                { "sendIt", new JmapEmailSubmission { EmailId = "#draft", IdentityId = identity.Id } }
            },
            OnSuccessDestroyEmail = new List<string>
            {
                "#sendIt"
            }
        }.Invoke("b");

        var emailCreateResponse = await jmap.SendRequest(emailSet, emailSubmissionSet);

        Console.WriteLine($"{Util.JsonStr(emailCreateResponse)}");
    }

    // query for the inbox, query and retrieve the 10 most recent emails
    internal static async Task TopTen(this JmapClient jmap, string accountId)
    {
        // get inbox
        var inboxQuery = new JmapMailboxQueryRequest(accountId)
        {
            Filter = new JmapMailboxQueryFilter { Role = "inbox", HasAnyRole = true }
        }.Invoke("a");

        var inboxQueryResponse = await jmap.SendRequest(inboxQuery);
        var inboxId = inboxQueryResponse
            ?.GetIds(inboxQuery)
            ?.SingleOrDefault() ?? throw new InvalidOperationException("couldn't get inbox ID");

        // query emails
        var emailQueryFilter = new JmapEmailQueryFilter { InMailbox = inboxId };
        var emailQuerySort = new List<JmapComparator> { JmapComparator.Desc(nameof(JmapEmail.ReceivedAt)) };
        var emailQueryLimit = 10;
        var emailGetProperties = new List<string> { "receivedAt", "subject" };

        var emailQuery = new JmapEmailQueryRequest(accountId)
        {
            Filter = emailQueryFilter,
            Sort = emailQuerySort,
            Limit = emailQueryLimit
        }.Invoke("a");

        var emailGet = new JmapEmailGetRequest(accountId)
        {
            References = new Dictionary<string, JmapResultReference>
            {
                { "#ids", emailQuery.GetRef("/ids/*") }
            },
            Properties = emailGetProperties
        }.Invoke("b");

        var emailResponse = await jmap.SendRequest(emailQuery, emailGet);

        var emails = emailResponse.GetItems<JmapEmail>(emailGet);

        foreach (var email in emails)
            Console.WriteLine($"{email.ReceivedAt} - {email.Subject}");
    }

    // same as above, but with high level helper methods
    internal static async Task TopTenWithHelpers(this JmapClient jmap)
    {
        // get inbox
        var inboxResults = await jmap.GetMailboxes(new JmapMailboxQueryFilter { Role = "inbox", HasAnyRole = true });
        var inbox = inboxResults.Single();

        // query emails
        var emailQueryFilter = new JmapEmailQueryFilter { InMailbox = inbox.Id };
        var emailQuerySort = new List<JmapComparator> { JmapComparator.Desc(nameof(JmapEmail.ReceivedAt)) };
        var emailQueryLimit = 10;
        var emailGetProperties = new List<string> { "receivedAt", "subject" };

        var emails = await jmap.GetEmails(emailQueryFilter, emailQuerySort, emailGetProperties, emailQueryLimit);

        foreach (var email in emails)
            Console.WriteLine($"{email.ReceivedAt} - {email.Subject}");
    }
}