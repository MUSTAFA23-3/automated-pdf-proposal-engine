/**
 * ============================================================================
 * Automated Lead-to-Proposal & PDF Invoice Generator (apps_script_pdf_mailer.gs)
 * Original Open-Source Showcase / Demonstration System
 * Author: Mustafa Mahmoud Tawfik
 * ============================================================================
 */

const PROPOSAL_CONFIG = {
  COMPANY_NAME: 'MMT Digital & Automation Studio',
  SENDER_TITLE: 'Mustafa Mahmoud Tawfik — Systems & Web Architect',
  DRIVE_FOLDER_NAME: 'Generated_Client_Proposals',
  ACCENT_HEX: '#2563EB',
  INK_HEX: '#0F172A'
};

/**
 * Triggered on Google Form submit or manual menu execution.
 * Generates a branded Light-Mode PDF proposal/invoice from the latest row
 * and emails it to the client while archiving a copy in Google Drive.
 * @param {Object} e - Optional form submit event.
 */
function generateAndSendProposalPDF(e) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getActiveSheet();
  const rowIndex = (e && e.range) ? e.range.getRow() : sheet.getLastRow();

  if (rowIndex < 2) {
    throw new Error('No client data row found.');
  }

  // Expected Columns: [0:Ref_ID, 1:Client_Name, 2:Company, 3:Email, 4:Service_Package, 5:Amount_USD, 6:Timeline_Days, 7:PDF_Status]
  const row = sheet.getRange(rowIndex, 1, 1, 8).getValues()[0];
  const refId = row[0] || ('PROP-' + Utilities.formatDate(new Date(), Session.getScriptTimeZone(), 'yyyyMMdd-HHmm'));
  const clientName = String(row[1] || 'Valued Partner');
  const company = String(row[2] || 'Client Organization');
  const email = String(row[3] || '').trim();
  const servicePkg = String(row[4] || 'Web & Automation Package');
  const amount = Number(row[5] || 0).toLocaleString('en-US', { style: 'currency', currency: 'USD' });
  const timeline = String(row[6] || '14 Days');

  if (!email) {
    throw new Error(`Row ${rowIndex} is missing a client email address.`);
  }

  const issueDate = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), 'MMMM dd, yyyy');

  const htmlTemplate = `
    <!DOCTYPE html>
    <html>
      <body style="font-family:Helvetica,Arial,sans-serif;color:${PROPOSAL_CONFIG.INK_HEX};margin:0;padding:36px;background:#FFFFFF;">
        <div style="border-top:6px solid ${PROPOSAL_CONFIG.ACCENT_HEX};padding-top:20px;">
          <table style="width:100%;margin-bottom:24px;">
            <tr>
              <td>
                <h1 style="margin:0;font-size:22px;color:${PROPOSAL_CONFIG.INK_HEX};">${PROPOSAL_CONFIG.COMPANY_NAME}</h1>
                <p style="margin:4px 0 0;font-size:12px;color:#64748B;">${PROPOSAL_CONFIG.SENDER_TITLE}</p>
              </td>
              <td style="text-align:right;">
                <span style="display:inline-block;background:#EFF6FF;color:${PROPOSAL_CONFIG.ACCENT_HEX};padding:6px 12px;border-radius:6px;font-weight:bold;font-size:12px;">
                  PROPOSAL / INVOICE #${refId}
                </span>
                <p style="margin:6px 0 0;font-size:12px;color:#64748B;">Issued: ${issueDate}</p>
              </td>
            </tr>
          </table>

          <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:8px;padding:16px;margin-bottom:24px;">
            <p style="margin:0;font-size:11px;text-transform:uppercase;color:#64748B;font-weight:bold;">Prepared For</p>
            <p style="margin:4px 0 0;font-size:15px;font-weight:bold;">${clientName} — ${company}</p>
            <p style="margin:2px 0 0;font-size:12px;color:#475569;">${email}</p>
          </div>

          <table style="width:100%;border-collapse:collapse;margin-bottom:28px;">
            <thead>
              <tr style="background:${PROPOSAL_CONFIG.INK_HEX};color:#FFFFFF;">
                <th style="padding:12px;text-align:left;font-size:12px;">Scope of Work / Service Package</th>
                <th style="padding:12px;text-align:left;font-size:12px;">Delivery SLA</th>
                <th style="padding:12px;text-align:right;font-size:12px;">Investment</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td style="padding:14px 12px;border-bottom:1px solid #E2E8F0;font-size:13px;">${servicePkg}</td>
                <td style="padding:14px 12px;border-bottom:1px solid #E2E8F0;font-size:13px;">${timeline}</td>
                <td style="padding:14px 12px;border-bottom:1px solid #E2E8F0;font-size:14px;font-weight:bold;text-align:right;color:${PROPOSAL_CONFIG.ACCENT_HEX};">${amount}</td>
              </tr>
            </tbody>
          </table>

          <p style="font-size:12px;color:#475569;line-height:1.6;">
            This proposal includes architecture setup, QA verification, documentation, and 14 days of post-launch support. Valid for 14 calendar days from issue date.
          </p>
        </div>
      </body>
    </html>
  `;

  // Convert HTML directly to PDF Blob
  const pdfBlob = Utilities.newBlob(htmlTemplate, 'text/html', `${refId}.html`)
    .getAs('application/pdf')
    .setName(`${refId}_${company.replace(/\s+/g, '_')}.pdf`);

  // Archive PDF in Google Drive
  const folder = getOrCreateFolder_(PROPOSAL_CONFIG.DRIVE_FOLDER_NAME);
  const savedFile = folder.createFile(pdfBlob);

  // Email PDF to client
  MailApp.sendEmail({
    to: email,
    subject: `Service Proposal & Invoice #${refId} — ${company}`,
    body: `Hello ${clientName},\n\nPlease find attached your formal service proposal and investment summary (${amount}) for ${servicePkg}.\n\nBest regards,\n${PROPOSAL_CONFIG.SENDER_TITLE}`,
    attachments: [pdfBlob]
  });

  // Update Sheet Status
  sheet.getRange(rowIndex, 8).setValue(`Sent (${issueDate}) | Drive ID: ${savedFile.getId()}`);
}

function getOrCreateFolder_(folderName) {
  const folders = DriveApp.getFoldersByName(folderName);
  return folders.hasNext() ? folders.next() : DriveApp.createFolder(folderName);
}
