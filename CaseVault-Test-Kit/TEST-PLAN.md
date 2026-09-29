# CaseVault v1.9 — step-by-step test with a mock case

Everything in this kit is **made up**: the case (2026-00123, *State v. Jordan Placeholder*), the people (Officer Alex Sample, Detective Casey Example, witness Robin Testperson), addresses, plates, the SSN (123-45-6789 is a well-known sample number), and the 555-01xx phone numbers. It's safe on any PC. Still, put it in a **test vault**, not your real one (step 0).

The folder **`2 - Screenshots`** shows what each step should look like. Its numbers match the `[#]` marks below. They were taken from the current v1.9 code in Chrome, with a stand-in for Ollama that has the same two models as you: Quick (`qwen2.5:7b`) and Light (a 3B model). A real model's AI flags will differ in wording, and sometimes in what it finds.

---

## 0. Before you start: make sure you're really on v1.9

If CaseVault looks different from the screenshots, you're almost certainly running an older copy.

| How you open it | How to update |
|---|---|
| **Installed app / hosted page (Chrome, Edge)** | Open it while online, wait for *"A CaseVault update was installed"*, then reload (Ctrl+R). Or press **Ctrl+Shift+R** once. |
| **Firefox via `W:\Start-CaseVault.bat`** | The helper shows the app copy in **`V:\CaseVault-App\`**, not the website, so it stays on the old version until you replace it. Download the ZIP from GitHub (Code → Download ZIP), replace the files in `V:\CaseVault-App\`, **and copy the new `tools\` files to W:** (v1.9 changed the helper). |

**Check:** click **Vault** (top right). *App version* must say **1.9.0**. The header must show a **🔒 Offline** pill, and a case must have a **Mail** tab. If not, you're on an older copy.

**Use a test vault.** In Chrome/Edge: Vault → *Open a different vault…* and pick an empty folder, for example `V:\CV-TEST\`, then **Create vault here**. In Firefox the helper always opens the real vault. Test in Chrome/Edge, or use a clearly named test case and delete it at the end (step 13).

---

## 1. The kit

`1 - Documents`:

| File | What it is | What it tests |
|---|---|---|
| `affidavit draft.docx` | The affidavit to check. It has **planted errors** (table below) | Word reading, the checker |
| `arrest report.pdf` | Normal text PDF | PDF text |
| `supp 2 - Det Example (scanned).pdf` | A **scanned** page (picture only) | OCR |
| `case report (XFA form).pdf` | An **Adobe LiveCycle (XFA)** form | XFA reading and preview |
| `drug exhibits log.xlsx` | Excel, two sheets | Spreadsheets |
| `vehicle info.csv` | CSV with plate, VIN, owner | CSV |
| `scene photo.png` | Photo of an evidence placard and a plate | Image OCR |
| `interview.wav` | 2-second tone | Recordings folder, audio player |
| `agency affidavit template.md` | A template using `{{case.*}}` and `{{affiant.*}}` | Templates, My details |
| `pii test text.txt` | Text full of personal details | Mail and online redaction |

### The planted errors (affidavit vs. reports)

| # | Affidavit says | Reports say | Should be flagged as |
|---|---|---|---|
| 1 | 21:**45** hours | 21**40** hours | **High · Time mismatch** (rules) |
| 2 | Officer Alex **Sampel** | Alex **Sample** | High · Name spelled differently. ⚠ **Currently missed**, see Findings |
| 3 | plate TST-**1248** | TST-**1284** | **High · Licence plate mismatch** (rules) |
| 4 | **three** shots | **two** shots | **High · Count mismatch** (rules) |
| 5 | $2,**45**0 | $2,**54**0 | **High · Amount mismatch** (rules) |
| 6 | ran **south** | ran **north** | Medium · Contradicted (AI, depends on the model) |
| 7 | **red** hooded sweatshirt | **dark** hooded sweatshirt (scanned supp) | Medium or Low (AI, depends on the model) |

**Traps that must *not* be flagged:** `1420 Example Ave.` vs `1420 Example Avenue` (same address), `03/14/2026` (same everywhere), `555-0142` (same), grey Toyota Camry (same).

---

## 2. Vault and My details — `[01]`–`[04]`

1. Open CaseVault, pick the test folder, click **Create vault here** `[01] [02] [03]`.
2. **Vault** → **My details (for templates)**: Name `Detective Casey Example`, Title `Detective`, Agency `Example County Test Unit`, Address (two lines) `100 Example Street` / `Testville, TX 00000`, Email `casey.example@agency.example`. Leave **Phone empty** on purpose `[04]`.
3. Look at the other Vault sections: Backups, Privacy screen, Online features, Always hide (PII watch list), Department mail, Outbound log, Templates, Maintenance.

## 3. The case — `[05]` `[06]`

1. **+ New case**: Title `State v. Jordan Placeholder`, Number `00123`, Client `Example County DA`, Opened `03/14/2026`, Tags `narcotics, firearm` `[05]`.
2. ✅ The address bar ends in `#/case/2026-00123/details`. The folder is named `<year>-<case no.>` `[06]`.

## 4. Files: folders and naming — `[07]`–`[09]`

1. **Files** tab: 14 document folders on the left `[07]`.
2. With **All documents** selected, choose all 8 documents (not the template or the `.txt`).
3. The dialog guesses each type from the file name `[08]`. Check or set: affidavit → Affidavits, arrest report → Arrest Report, supp 2 → Supplementary Report (type `Det. Example` as the description), case report → Case Report, exhibits → Drug Exhibits, vehicle → Vehicle Information, interview → Recordings, photo → Other.
4. ✅ *Saved as* shows `2026-00123 Arrest Report.pdf`, `2026-00123 Supplementary Report - Det. Example.pdf` and so on. After **Save to SSD** each file is in its folder, with a count per folder `[09]`.
5. In File Explorer, open `CaseVault-Data\cases\2026-00123\files\`: the same folders and names are on the SSD.

## 5. Previews — `[10]`–`[14]`

1. **Case Report.pdf** → the XFA form is drawn inside CaseVault, not *"Please wait…"* `[10]`. Click **Show filled-in fields** for the list: case number, offense, officer, location, plate, three *Timeline row* lines. The signature image is left out `[11]`.
2. **Supplementary Report** → shows the scanned page `[12]`.
3. **Drug Exhibit.xlsx** → a table with sheet tabs *Exhibits* and *Chain of custody* `[13]`.
4. **Recording.wav** → an audio player. **Other.png** → the photo `[14]`.
5. Open the same XFA PDF in Edge's own PDF viewer: it only says *"Please wait…"*. That's why CaseVault reads the form itself.

## 6. Notes and timeline — `[15]` `[16]`

1. **Notes**: type a few lines with `**bold**` and `- bullets`, then click **Preview** `[15]`.
2. **Timeline**: add two events (03/14/2026 21:40 *Shots fired call*, 23:05 *Arrest*) and a **Deadline** 3 days from today (*File affidavit with the court*) `[16]`.
3. ✅ The deadline appears under the case in the left list (*in 3 days*, amber) and on the **Overview**.

## 7. Consistency check — `[17]`–`[20]`

1. **Checks** tab. *Document to check*: **Affidavits/2026-00123 Affidavit.docx**. All reports are ticked. Tick **Include AI review** `[17]`.
2. **Run check** `[18]`. Watch:
   - each document being read; the scanned supp and the photo go through OCR (amber tick);
   - the header: **the moving bars and "Checking 3 of 8"**. The first statement can show **Loading model…** for 10–30 s;
   - the window: *This statement: 7 s · about 1:10 left*.
3. Results `[19]`. ✅ There must be **4 High rule flags**: time 21:45 vs 2140, plate TST-1248 vs TST-1284, three vs two shots, $2,450 vs $2,540. ✅ There must be **no** flag for the address, date, phone or car.
   AI flags (Medium) for *south vs north* and possibly the hoodie depend on the model: qwen2.5:7b usually finds *north/south*. With the 3B model, expect fewer and less reliable AI flags.
4. The document list says *XFA form* for the case report, and *OCR was used* for the supp and the photo.
5. Click a quote → the document opens with the sentence highlighted `[20]` → **Open original**.
6. Mark flags **Fix** / **Not an issue** / **Explained**, then use the filters.
7. Optional: open the check again (Checks → the run) and try **Delete this check** (it asks first).

## 8. Templates and drafts — `[21]`–`[28]`

1. **Vault → Templates → Import .md…** → pick `agency affidavit template.md`. It opens in the editor: click **Save** `[21] [22]`.
2. **Drafts** → New draft, type *Affidavit*, **From a template** → *Affidavit — {{case.title}}* → **Create draft** `[23]`.
   ✅ Your name, title, agency and 2-line address are filled in. ✅ Phone shows `[CONFIRM: affiant.phone]`. The **To confirm** panel lists every `[CONFIRM: …]`. Click one to jump to it.
3. **AI suggestion box**: at the end of the last line, type `3. On March 14, 2026, Officer Alex Sample` and pause. A box labelled **AI suggestion** appears just under the line `[24]`. **Tab** accepts, **Esc** dismisses. Also try it scrolled halfway down a long draft, in Firefox and in Chrome.
4. **Draft with AI**: new draft → *Draft with AI* → tick the documents → **Generate** `[25]`. The header shows **Drafting…** with the bars `[26]`, and the text streams in. The result has the yellow *AI-generated draft* banner `[27]`.
   ✅ While it's writing, suggestions pause. If you start a check meanwhile, it says it's waiting.
5. Open the affidavit draft → **Run consistency check** `[28]`. The same checker runs on the draft.
6. **Export → Save .docx to case files**: the Word file lands in the Affidavits folder. Open it in Word: the `[CONFIRM: …]` placeholders are highlighted yellow.

## 9. Department mail — `[29]`–`[34]`

1. **Mail** tab → *Set up department mail first* `[29]` → **Open mail settings…**
   - Allowed domains: `agency.example`
   - Address book: `Narcotics Unit <narcotics-unit@agency.example>`
   - Subject marking: `[LES]` `[30]`
2. Back on **Mail**: To = `someone@gmail.com` → ✅ **⛔ outside the department** `[31]`.
3. To = `narcotics-unit@agency.example`. Subject `[LES] 2026-00123 – arrest report for review`. Paste `pii test text.txt` into the message. Attach **Arrest Report.pdf** (expand its folder group) `[32]`.
4. **Check & create Outlook draft** → the review lists the DOB, SSN, licence, VIN and case number, and **asks you to type SEND** `[33]`. Tick *I have checked…*, then continue.
5. ✅ *Outlook draft ready*: `files\Email\2026-00123 Email - arrest report for review.eml` `[34]`. Double-click it in File Explorer: classic Outlook opens a new email with the PDF attached. **Don't send it**; close without saving.
6. **Vault → Outbound log** lists the hand-off (never the text).

## 10. Online research (review screen only) — `[35]`–`[37]`

> Only if your agency allows cloud AI. You can do this test without sending anything: stop at the review screen and click Cancel.

1. **Vault → Online features → Allow going online**. Under **Always hide**, add `Robin Testperson` and `Jordan Placeholder`.
2. Click **🔒 Offline** in the header → the research page `[35]` → **Go online** → confirm. The pill turns **Online · 15 min**.
3. Service *claude.ai*, purpose *Research*, case *2026-00123*. Paste a question plus `pii test text.txt` `[36]` → **Check, copy & open claude.ai**.
4. Open **Exactly what will be sent** `[37]`. ⚠ Look closely. In v1.9 the **plate `TST-1284`, the phone `555-0142`, part of the address and part of the email are NOT hidden**. See Findings #1. **Cancel**, then **Go offline**.

## 11. Header tools — `[38]` `[39]` `[40]`

1. **Memory indicator** (`App … MB`): hover over it `[38]`. With `Start-CaseVault.bat` running it also shows RAM, AI (GPU/CPU split of the loaded model) and free space on the CASEVAULT drive. **Free AI memory** unloads the model.
2. **Privacy screen**: `Ctrl+Shift+H` or Esc Esc → grey screen, tab title *New Tab* `[39]`. Click to return. Then set a PIN under Vault → Privacy screen and try again.
3. **Case list**: `Ctrl+\` collapses it to a thin strip `[40]`; `Ctrl+\` again restores it.

## 12. Archive and restore — `[41]` `[42]`

1. **Details → Case actions → Archive case…** → confirm. The case moves under **Archived (1)** and opens read-only with a banner `[41]`. On the SSD it is now in `CaseVault-Data\archive\2026-00123\`.
2. Check that files still open, drafts and checks can be read, and nothing can be edited.
3. **Restore to active cases** → back in the list, status *Open*. The **Overview** shows the counts, the deadline and recent cases `[42]`.

## 13. Clean up

**Details → Delete case…** → type `00123` → **Delete permanently**. (*Archive instead* is offered in the same window.) In the test vault you can also just delete the `V:\CV-TEST` folder.

## 14. On each PC

| Check | Beelink (RTX 3050) | L14 (no NVIDIA GPU) |
|---|---|---|
| Header after starting `W:\Start-CaseVault.bat` | `AI: Connected (Quick · qwen2.5:7b)` | ⚠ **also** `Quick · qwen2.5:7b` under *Auto*, which runs on the CPU and is slow. Click the AI pill and choose **Light** (see Findings #2). |
| Memory indicator → AI | 100% GPU | CPU only |
| Check with AI, 8 statements | about 5–20 s per statement | expect much slower with Quick; use Light |
| Suggestions | smallest model (Light), quick | quick with Light |

---

## Findings from this walkthrough — fixed in v1.9.1

All the findings below are fixed in **CaseVault 1.9.1** ([t3rminal-cmd/casevault#9](https://github.com/t3rminal-cmd/casevault/pull/9); the "null" fix is #8). The screenshots in `2 - Screenshots` were retaken with 1.9.1. Screenshots 43–45 show the new parts.

| # | Found in v1.9 | In v1.9.1 |
|---|---|---|
| 1 | 🔴 Online redaction leaked the plate, a 7-digit phone number, and parts of addresses/emails that contained a known name | Overlaps are merged, so the whole address or email is hidden. 7-digit phones and plates without "plate" are found. Step 10 now shows `[PLATE_1]`, `[ADDRESS_1]`, `[PHONE_1]`, `[EMAIL_1]` |
| 2 | 🟠 *Sampel* vs *Sample* not flagged | Flagged (High), with the Arrest Report as the source. Step 7 now expects **5** High rule flags |
| 3 | 🟡 `00123` vs `2026-00123` flagged | Treated as the same number |
| 4 | 🟡 `… Affidavit - Affidavit - …` export name | `2026-00123 Affidavit - arrest warrant.docx` |
| 5 | 🟡 "null" above check results | Gone |
| — | Auto ran the 7B model on the L14 | **AI profile per PC.** Auto uses Light where the AI runs on the processor `[43] [44]` |
| — | Template lines flagged "not found" | Your own details and today's date are ignored |
| — | Cramped Files dates | Short dates (`28 Sep 22:48`) |
| — | — | New **Vault → Maintenance → Run self-test** (13 checks) `[45]` |

### Updated expectations for v1.9.1

- **Step 7:** 5 High rule flags: time, **name (Sampel/Sample)**, plate, count, amount.
- **Step 10:** *Exactly what will be sent* contains no `TST-1284`, `1420`, `555-0142` or any part of the email.
- **Step 14 (L14):** the header shows **Light**, either straight away or after the first AI request with *"This PC runs the AI on its processor…"*. Click **AI:** → *Profile on this PC* for the reason. Choosing a profile on one PC doesn't change the other.
- **New step 15, self-test:** Vault → Maintenance → **Run self-test…** → all ✓ on both PCs (**!** on passage search until nomic-embed-text is installed).

## Adding nomic-embed-text (passage search) — short version

1. Start `W:\Start-CaseVault.bat` and leave its window open.
2. Windows key + R → `cmd` → Enter.
3. `W:\ollama\ollama.exe pull nomic-embed-text` → Enter → wait for **success** (~270 MB; needs internet once).
4. `W:\ollama\ollama.exe list` shows `nomic-embed-text:latest`.
5. CaseVault → click **AI:** → **Check again** → ✓ *Passage search: nomic-embed-text:latest*.

Once on W:, both PCs use it. The full version is in CaseVault's `docs/AI-SETUP.md` → *Adding nomic-embed-text*.
