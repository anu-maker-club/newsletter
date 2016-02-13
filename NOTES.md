# Notes on sending email

## Image compatibility

We had a lot of trouble getting images to display when Darren went to send
messages. Originally we were using [`cid:`
embedding](http://stackoverflow.com/q/4018709) in `render.py`. That method is
reported to work in the majority of email clients, but I found that the
resultant messages would:

1. Show up in Thunderbird, when they were in the inbox of a GMail account.
2. *Not* show up in Thunderbird when they were in the inbox of an ANU account.
3. Show up in Thunderbird when forwarded from an ANU account to a GMail
   account!
4. Not show up at all in the GMail web interface or ANU webmail interface. The
   GMail interface in particular had an annoying habit of replacing the images
   with an image of the alt-text which was the wrong width, thereby breaking the
   layout slightly.

Needless to say, this was rather confusing. We tried using the sender's email
domain as the CID domain, and also tried changing the `Content-Disposition` of
the attached images from `inline` to `attachment`, but to no avail.

After giving up on CID embedding, I tried just normal `data:` URL embedding
(with Base64-encoded PNG images). This produced more favourable results:

1. The images showed up in Thunderbird, regardless of which inbox they were in.
2. Images were initially blocked on ANU's webmail (office.com), but the webmail
   interface showed a prompt which let the user unblock the images, at which
   point all images displayed properly.
3. GMail's web interface blocked images completely for me (including the
   breaking alt-text display), even after adding the sender to my contacts.
   Darren found that GMail displayed the images without prompting. This may be
   because of differences in how we added the sender to our contacts.

Due to these results, `data:` embedding is the method we're using at the moment.
