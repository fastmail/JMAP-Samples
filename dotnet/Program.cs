using JmapNet;
using JmapNet.Client;
using JmapSamples;

// initialize the client
var hostName = Environment.GetEnvironmentVariable("JMAP_HOSTNAME") ?? "api.fastmail.com";
var userName = Environment.GetEnvironmentVariable("JMAP_USERNAME") ?? throw new InvalidOperationException("no user name");
var token = Environment.GetEnvironmentVariable("JMAP_TOKEN") ?? throw new InvalidOperationException("no token");

using var jmap = await JmapClient.Init(new Uri($"https://{hostName}"), token)
                 ?? throw new InvalidOperationException("couldn't initialize client");

var accountId = jmap.Session.PrimaryAccounts[JmapConstants.JmapMailCapability];

// programs
await jmap.HelloWorld(accountId, userName);
await jmap.TopTen(accountId);
await jmap.TopTenWithHelpers();
