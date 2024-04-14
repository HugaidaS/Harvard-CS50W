document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => show_emails('inbox'));
  document.querySelector('#sent').addEventListener('click', () => show_emails('sent'));
  document.querySelector('#archived').addEventListener('click', () => show_emails('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // By default, load the inbox
  show_emails('inbox');
  removeSubmissionListener()
});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
  addSubmissionListener()
}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;
}

function send_email(event){
  console.log('Form submitted...');
  event.preventDefault();
  // Get the values of the form fields
  const recipients = document.querySelector('#compose-recipients').value;
  const subject = document.querySelector('#compose-subject').value;
  const body = document.querySelector('#compose-body').value;

  // Send the email
  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
      recipients: recipients,
      subject: subject,
      body: body
    })
  })
  .then(response => response.json())
  .then(result => {
    if (result.error) {
      showError(result.error);
      return;
    }
    console.log(result);
  });

  show_emails('sent');
}

function addSubmissionListener() {
  console.log('Listening for submission...');
  const form = document.querySelector('#compose-form');

  // Add event listener to the form when it is submitted

  form.addEventListener('submit', evt => send_email(evt));
}

function removeSubmissionListener() {
  console.log('Removing submission listener...');
  const form = document.querySelector('#compose-form');

  form.removeEventListener('submit', evt => send_email(evt));
}

function render_row(email, currentUser) {
  const emailBox = document.createElement('div');
  emailBox.className = `email-box border p-3 mb-3 d-flex justify-content-between ${email.read ? 'bg-light' : 'bg-white'}`;
  const emailContent = document.createElement('div');
  emailContent.innerHTML = `
    <div class="email-box-sender font-weight-bold">To: ${email.recipients}</div>
    <div class="email-box-subject mt-2">Subject: ${email.subject}</div>
    <div class="email-box-timestamp text-muted mt-1">Date: ${email.timestamp}</div>
  `;
  emailBox.appendChild(emailContent);

  if (email.recipients.includes(currentUser)) {
    const archiveButton = document.createElement('button');
    archiveButton.className = 'btn btn-sm btn-outline-primary';
    archiveButton.innerText = email.archived ? 'Unarchive' : 'Archive';
    archiveButton.onclick = (event) => archive_email(event, email, archiveButton);
    emailBox.appendChild(archiveButton);
  }

  return emailBox;
}

function archive_email(event, email, button) {
  event.stopPropagation();
  fetch(`/emails/${email.id}`, {
    method: 'PUT',
    body: JSON.stringify({
      archived: !email.archived
    })
  })
  .then(() => {
    email.archived = !email.archived;
        button.innerText = email.archived ? 'Unarchive' : 'Archive';
        show_emails('inbox');
  });
}


function render_list(emails) {
  const currentUser = document.querySelector('h2').innerText;
  const box = document.querySelector('#emails-view');
  emails.forEach(email => {
    const emailBox = render_row(email, currentUser);
    emailBox.addEventListener('click', () => showEmail(email.id));
    box.appendChild(emailBox);
  });
}

function show_emails(mailbox) {
  load_mailbox(mailbox);
  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
    render_list(emails);
  });
}

function showEmail(id) {
  console.log('Showing email...');
  fetch(`/emails/${id}`)
  .then(response => response.json())
  .then(email => {
    if(email.error){
      showError(email.error);
      return;
    }
    load_mailbox(email.subject);
    const emailContainer = document.createElement('div');
    emailContainer.className = 'email-box border p-3 mb-3';
    // with archive and reply button
    emailContainer.innerHTML = `
      <div class="email-box-sender font-weight-bold">From: ${email.sender}</div>
      <div class="email-box-subject mt-2">Subject: ${email.subject}</div>
      <div class="email-box-timestamp text-muted mt-1">Date: ${email.timestamp}</div>
      <div class="email-box-body mt-3">${email.body}</div>
    `;
    document.querySelector('#emails-view').appendChild(emailContainer);

    const replyButton = document.createElement('button');
    replyButton.className = 'btn btn-sm btn-outline-primary mr-2 mt-3';
    replyButton.innerText = 'Reply';
    replyButton.onclick = () => reply_email(email);

    const archiveButton = document.createElement('button');
    archiveButton.className = 'btn btn-sm btn-outline-primary mt-3';
    archiveButton.innerText = email.archived ? 'Unarchive' : 'Archive';
    archiveButton.onclick = (event) => archive_email(event, email, archiveButton);

    emailContainer.appendChild(replyButton);
    emailContainer.appendChild(archiveButton);

    if (!email.read) {
      console.log('Registering as read...');
      registerAsRead(email);
    }
  });
}


function reply_email(email) {
  compose_email();
  document.querySelector('#compose-recipients').value = email.sender;
  document.querySelector('#compose-subject').value = email.subject.startsWith('Re:') ? email.subject : `Re: ${email.subject}`;
  document.querySelector('#compose-body').value = `On ${email.timestamp} ${email.sender} wrote: ${email.body}`;
}

function registerAsRead(email) {
  fetch(`/emails/${email.id}`, {
    method: 'PUT',
    body: JSON.stringify({
      read: true
    })
  });
}

function showError(message) {
  alert(message);
}