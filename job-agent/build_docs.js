// Usage (from the kit folder): node job-agent/build_docs.js job-agent/output/jobs/<slug>.json   (needs: npm install, LibreOffice 'soffice', poppler 'pdfinfo')
// Renders a one-page Australian-format resume + cover letter from tailored text (job.json) and profile.json.
// Content (profile, bullets, paragraphs) is written by the agent from VERIFIED profile facts only.
const fs = require('fs');
const { execSync } = require('child_process');
const { Document, Packer, Paragraph, TextRun, AlignmentType, LevelFormat, BorderStyle, TabStopType } = require('docx');

const profile = JSON.parse(fs.readFileSync(__dirname + '/profile.json', 'utf8'));
const job = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const FONT = 'Calibri', NAVY = '1F3A5F';
const outDir = __dirname + '/output';
fs.mkdirSync(outDir, { recursive: true });

// ---------- RESUME ----------
const W = 11906 - 2000;
const r = (t, o = {}) => new TextRun({ text: t, font: FONT, size: 21, ...o });
const heading = (t) => new Paragraph({ spacing: { before: 150, after: 60 },
  border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: NAVY, space: 2 } },
  children: [r(t.toUpperCase(), { bold: true, color: NAVY, size: 23 })] });
const bullet = (t) => new Paragraph({ numbering: { reference: 'b', level: 0 }, spacing: { after: 40 }, children: [r(t)] });
const roleLine = (a, b) => new Paragraph({ spacing: { before: 100, after: 0 }, tabStops: [{ type: TabStopType.RIGHT, position: W }],
  children: [r(a, { bold: true }), r('\t' + b, { bold: true })] });
const orgLine = (t) => new Paragraph({ spacing: { after: 50 }, children: [r(t, { italics: true })] });

const R = job.resume;
const rc = [
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 40 }, children: [r(profile.name.toUpperCase(), { bold: true, size: 36, color: NAVY })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 20 }, children: [r(`${profile.location}  |  ${profile.phone}  |  ${profile.email}`)] }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [r(R.work_rights_line, { size: 19 })] }),
  heading('Career Profile'),
  new Paragraph({ spacing: { after: 40 }, children: [r(R.profile)] }),
  heading('Key Skills'), ...R.skills.map(bullet),
  heading('Work Experience'),
];
for (const e of R.experience) { rc.push(roleLine(e.title, e.dates), orgLine(e.org), ...e.bullets.map(bullet)); }
rc.push(heading('Education'));
for (const e of profile.education) { rc.push(roleLine(e.degree, e.dates), orgLine(e.detail)); }
rc.push(heading('Licences, Certificates and Technical Skills'));
rc.push(new Paragraph({ spacing: { after: 30 }, children: [r('Certificates: ', { bold: true }), r(R.certificates.join('  |  '))] }));
rc.push(new Paragraph({ spacing: { after: 30 }, children: [r('Languages: ', { bold: true }), r(R.languages || profile.languages || ''), r('   |   '), r('Systems: ', { bold: true }), r(R.systems || profile.systems || '')] }));
if (R.extra_line) rc.push(new Paragraph({ spacing: { after: 30 }, children: [r(R.extra_line.label + ': ', { bold: true }), r(R.extra_line.text)] }));
rc.push(heading('Referees'), new Paragraph({ children: [r('Available on request')] }));

const numbering = { config: [{ reference: 'b', levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 360, hanging: 260 } } } }] }] };
const resumeDoc = new Document({ styles: { default: { document: { run: { font: FONT, size: 21 } } } }, numbering,
  sections: [{ properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 560, bottom: 560, left: 1000, right: 1000 } } }, children: rc }] });

// ---------- COVER LETTER ----------
const c = (t, o = {}) => new TextRun({ text: t, font: FONT, size: 22, ...o });
const p = (t, after = 160) => new Paragraph({ spacing: { after, line: 276 }, children: [c(t)] });
const C = job.cover;
const cc = [
  new Paragraph({ spacing: { after: 40 }, children: [c(profile.name.toUpperCase(), { bold: true, size: 32, color: NAVY })] }),
  new Paragraph({ spacing: { after: 200 }, border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: NAVY, space: 4 } },
    children: [c(`${profile.location}  |  ${profile.phone}  |  ${profile.email}`, { size: 20 })] }),
  new Paragraph({ spacing: { after: 160 }, children: [c(job.date)] }),
  ...C.recipient.map((l, i) => new Paragraph({ spacing: { after: i === C.recipient.length - 1 ? 200 : 0 }, children: [c(l)] })),
  new Paragraph({ spacing: { after: 160 }, children: [c('Dear Hiring Manager,')] }),
  new Paragraph({ spacing: { after: 160 }, children: [c('Re: ' + C.subject, { bold: true })] }),
  ...C.paragraphs.map(t => p(t)),
];
if (C.bullets && C.bullets.length) {
  cc.push(p(C.bullets_intro || 'I believe I would be a strong fit because:', 100));
  C.bullets.forEach((t, i) => cc.push(new Paragraph({ spacing: { after: i === C.bullets.length - 1 ? 160 : 60 }, indent: { left: 360, hanging: 260 }, children: [c('•  ' + t)] })));
}
cc.push(p(C.closing), p('Thank you for your time and consideration.'),
  new Paragraph({ spacing: { after: 480 }, children: [c('Yours sincerely,')] }),
  new Paragraph({ children: [c(profile.short_name, { bold: true })] }));
const coverDoc = new Document({ styles: { default: { document: { run: { font: FONT, size: 22 } } } },
  sections: [{ properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1000, bottom: 1000, left: 1200, right: 1200 } } }, children: cc }] });

(async () => {
  const base = `${outDir}/${profile.short_name.replace(/[^A-Za-z0-9]+/g, '_')}_`;
  const files = { resume: `${base}Resume_${job.slug}.docx`, cover: `${base}Cover_Letter_${job.slug}.docx` };
  fs.writeFileSync(files.resume, await Packer.toBuffer(resumeDoc));
  fs.writeFileSync(files.cover, await Packer.toBuffer(coverDoc));
  execSync(`soffice --headless --convert-to pdf --outdir "${outDir}" "${files.resume}" "${files.cover}"`, { stdio: 'ignore' });
  const pages = (f) => parseInt(execSync(`pdfinfo "${f.replace('.docx', '.pdf')}" | grep Pages`).toString().split(':')[1]);
  const rp = pages(files.resume), cp = pages(files.cover);
  console.log(JSON.stringify({ resume_pdf: files.resume.replace('.docx', '.pdf'), cover_pdf: files.cover.replace('.docx', '.pdf'), resume_pages: rp, cover_pages: cp, ok: rp === 1 && cp === 1 }));
  if (rp !== 1 || cp !== 1) process.exit(2);
})();
