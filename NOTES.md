# Notes on sending email

## Image compatibility

We had a lot of trouble getting images to display when Darren went to send
messages. Originally I was using [`cid:`
embedding](http://stackoverflow.com/q/4018709) in `render.py`. That method is
reported to work in the majority of email clients, but I found that the
resultant messages would:

1. Show up in Thunderbird, when they were in the inbox of a GMail account.
2. *Not* show up in Thunderbird when they were in the inbox of an ANU account.
3. Show up in Thunderbird when forwarded from an ANU account to a GMail
   account!
4. Not show up at all in the GMail web interface or ANU webmail interface.

Needless to say, this was rather confusing. We tried using the sender's email
domain as the CID domain, and also tried changing the `Content-Disposition` of
the attached images from `inline` to `attachment`, but to no avail.
