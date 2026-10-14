# G34 – Bounded reproduction of Byam
 
Evidence repository for group G34's bounded reproduction of:
 
> Reyes et al. (2026). *Byam: Fixing Breaking Dependency Updates with Large Language Models.*
> Empirical Software Engineering 31:113. https://doi.org/10.1007/s10664-026-10835-1
> Code: https://github.com/chains-project/bacardi · Dataset: https://github.com/chains-project/bump
 
Our research questions, sample and decision rules are in **`M1.md`** (frozen at git tag `m1-frozen`).
Anything changed after the freeze is in **`deviations.md`**.
 
---
 
## What's in this repo
 
| Folder / file | What it holds |
|---|---|
| `M1.md` | Our frozen plan: RQs, sample, method, decision rule |
| `deviations.md` | Every change made after M1 was frozen |
| `env/` | Exact bacardi/bump commits, each runner's tool versions, build log, OpenRouter activity |
| `sample/` | Our 12 cases (`g34-sample.txt`), how they were chosen, case details, Docker image digests |
| `config/` | The `.env` used for each run, with API keys removed |
| `runs/` | Raw output of every run (`pilot/`, `p1/`, `p8/`, `opus-p1/`, `opus-p8/`) |
| `derived/` | Scripts and numbers calculated from the raw output, and the final comparison |
 
The tool code (bacardi) and dataset (bump) are **not** in this repo. You clone them separately (see setup).
 
---
 
## Setup (do this once)
 
Everything runs in **Linux**. On Windows that means **WSL2 Ubuntu**, not Git Bash or PowerShell.
Copy each box into the Ubuntu window and press Enter.
 
### 1. Get Ubuntu (Windows only)
In **PowerShell**:
```powershell
wsl --install -d Ubuntu
```
Restart if asked, then open the **Ubuntu** app and pick a username + password.
(If it says "already exists", you already have it, so just open Ubuntu.)
 
### 2. Install the tools
```bash
sudo apt update
sudo apt install -y openjdk-21-jdk maven git jq python3-venv python3-pip gh
java -version     # should say 21
```
 
### 3. Install Docker
```bash
cd ~
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```
⚠️ It shows a warning and waits 20 seconds. **Don't press anything**, just let it finish.
```bash
sudo usermod -aG docker $USER
exit
```
Then in **PowerShell**: `wsl --shutdown`, and open Ubuntu again. Check it works:
```bash
docker run --rm hello-world     # should print "Hello from Docker!"
```
 
### 4. Set up git
Use the **same email as your GitHub account**, or your commits won't show up as yours.
```bash
git config --global user.name "Your Name"
git config --global user.email "your-github-email@example.com"
gh auth login      # GitHub.com → HTTPS → Yes → Login with a web browser
```
 
### 5. Download everything
Work in `~/g34` inside Ubuntu, **not** in `/mnt/c/...` (your Windows files).
```bash
mkdir -p ~/g34/work && cd ~/g34
git clone https://github.com/brihannaenright/g34-byam-repro.git
git clone https://github.com/chains-project/bacardi.git
git -C bacardi checkout 4bc6b254dea54a70ed9cbac32836cddc38ee6e4a
git clone https://github.com/chains-project/bump.git
git -C bump checkout 324d5513aa5ca40b5cb32de5b816a58fa60bd7bb
```
 
### 6. Set up Python
This makes a private box of Python packages that bacardi needs (a "virtual environment").
```bash
python3 -m venv ~/byam-venv
source ~/byam-venv/bin/activate
pip install requests python-dotenv openai anthropic google-generativeai
```
 
### 7. Make every new terminal ready automatically
```bash
echo 'E=~/g34/g34-byam-repro' >> ~/.bashrc
echo 'source ~/byam-venv/bin/activate' >> ~/.bashrc
source ~/.bashrc
```
You should now see `(byam-venv)` at the start of the line. `$E` is now a shortcut to this repo.
 
### 8. Build bacardi
```bash
cd ~/g34/bacardi
mvn clean install
ls core/target/Bump.jar     # this file must exist
```
 
### 9. Record your computer's setup
Change `yourname` to your name:
```bash
N=yourname
{ uname -a; echo; java -version 2>&1; echo; mvn -v; echo; docker version; echo; python3 --version; } > $E/env/versions-$N.txt 2>&1
pip freeze > $E/env/pip-freeze-$N.txt
cd $E && git pull && git add env && git commit -m "Environment for $N" && git push
```
 
---
 
## Running the experiments
 
**Before every run:** say in the group chat which run you're doing, so nobody doubles up.
 
You need the API key (ask the group). It **only** ever goes in `~/g34/bacardi/.env`.
That file is not in this repo. **Never commit it or paste the key anywhere.**
 
### Run 1: DeepSeek P1
 
**a) Make the settings file.** Paste the whole box:
```bash
N=yourname
cd ~/g34/bacardi
CASES=$(paste -sd, $E/sample/g34-sample.txt)
cat > .env <<EOF
BENCHMARK_PATH=$HOME/g34/bump/data/benchmark
APIDIFF_FILE=$HOME/g34/bacardi/analysis/api_diff.txt
JAVA_VERSION_INCOMPATIBILITY_FILE=$HOME/g34/bacardi/analysis/java_version_incompatibility.txt
PYTHON_SCRIPT=$HOME/g34/bacardi/llm/call_llm.py
PROJECTS_PATH=$HOME/g34/work/projects-p1
OUTPUT_PATH=$HOME/g34/g34-byam-repro/runs/p1
LLM_TYPE=openrouter
LLM=deepseek/deepseek-chat
OPENROUTER_API_KEY=PASTE_KEY_HERE
OPENROUTER_PROVIDER=
LLM_TEMP=0
MAX_ATTEMPT=1
PIPELINE=BASELINE
RESTART=true
SPECIFIC_FILE=$CASES
EOF
```
 
**b) Add the key.**
```bash
nano .env
```
Replace `PASTE_KEY_HERE` with the key (right-click pastes). Save with **Ctrl+O**, **Enter**, then exit with **Ctrl+X**.
 
**c) Start it.**
```bash
sed -E 's/^((OPENROUTER_)?API_KEY|GOOGLE_API_KEY|ANTHROPIC_API_KEY)=.*/\1=REDACTED/' .env > $E/config/env.p1.redacted
echo "Run by $N (started $(date -Iseconds))" > $E/runs/p1/command.txt
java -jar core/target/Bump.jar 2>&1 | tee $E/runs/p1/run.log
```
This takes a long time (maybe 1–2 hours). **Leave the window open and don't let the laptop sleep.**
It's finished when the text stops and you can type again.
 
😌 `ERROR ... Repository HEAD is null` and `Could not stop container Status 304` are normal. Ignore them.
 
**d) Check it worked.**
```bash
jq 'keys | length' $E/runs/p1/deepseek-deepseek-chat/result_repair_deepseek-deepseek-chat.json
```
✅ Should say **12**. ❌ Anything else → stop and tell the group.
 
**e) Save it.**
```bash
cp ~/g34/bacardi/costs_*.json $E/runs/p1/ 2>/dev/null
cd $E && git pull && git add -A && git diff --cached | grep -n "sk-or-" && echo "STOP: key staged" || git commit -m "P1 run (DeepSeek): 12 cases"
git push
```
❌ If it prints **STOP: key staged**, don't push. Tell the group.
 
### Run 2: DeepSeek P8
 
**a) Change the settings.** (It needs a **new** projects folder, or the extra API-change info gets skipped.)
```bash
cd ~/g34/bacardi
sed -i "s#^PROJECTS_PATH=.*#PROJECTS_PATH=$HOME/g34/work/projects-p8#; s#^OUTPUT_PATH=.*#OUTPUT_PATH=$HOME/g34/g34-byam-repro/runs/p8#; s#^PIPELINE=.*#PIPELINE=BASELINE_COT_API_DIFF_BUGGY#; s#^RESTART=.*#RESTART=true#" .env
grep -E 'PROJECTS_PATH|OUTPUT_PATH|PIPELINE' .env
```
✅ Should show `projects-p8`, `runs/p8` and `BASELINE_COT_API_DIFF_BUGGY`.
 
**b) Start it.**
```bash
sed -E 's/^((OPENROUTER_)?API_KEY|GOOGLE_API_KEY|ANTHROPIC_API_KEY)=.*/\1=REDACTED/' .env > $E/config/env.p8.redacted
echo "Run by $N (started $(date -Iseconds))" > $E/runs/p8/command.txt
java -jar core/target/Bump.jar 2>&1 | tee $E/runs/p8/run.log
```
 
**c) Check it worked.**
```bash
jq 'keys | length' $E/runs/p8/deepseek-deepseek-chat/result_repair_deepseek-deepseek-chat.json
grep -rl "The error is caused by a change in the API" $E/runs/p8/deepseek-deepseek-chat/ | head
```
✅ First should say **12**, second should list some files. ❌ Otherwise → stop and tell the group.
 
**d) Save it.**
```bash
cp ~/g34/bacardi/costs_*.json $E/runs/p8/ 2>/dev/null
cd $E && git pull && git add -A && git diff --cached | grep -n "sk-or-" && echo "STOP: key staged" || git commit -m "P8 run (DeepSeek): 12 cases"
git push
```
 
**e) Save the OpenRouter record.** On openrouter.ai → **Activity**, export (or screenshot) and save as
`env/openrouter-activity-deepseek.csv` (or `.png`). Commit and push.
 
### Runs 3 and 4: Claude Opus P1 and P8
 
Same steps as Runs 1 and 2, but in `.env`:
- `LLM_TYPE=anthropic`
- `LLM=` the exact Claude Opus model ID
- `ANTHROPIC_API_KEY=` the Anthropic key (instead of `OPENROUTER_API_KEY`)
- add `MAX_TOKEN=8192` (bacardi crashes without it)
- folders: `projects-opus-p1` / `runs/opus-p1` and `projects-opus-p8` / `runs/opus-p8`
Before the full runs: do a one-case pilot into `runs/opus-pilot/`. If any bacardi code has to change to make Opus work,
save the change with `git -C ~/g34/bacardi diff > $E/config/opus-refactor.patch`, add a row to `deviations.md`, and commit both **before** running.
The results folder will be named after the model ID instead of `deepseek-deepseek-chat`.
 
---
 
## Reading the results
 
Each run writes `runs/<run>/<model>/result_repair_<model>.json`, with one entry per case.
The `failureCategory` says what happened after the AI's fix was applied:
 
| `failureCategory` | Meaning | Counts as fixed? |
|---|---|---|
| `BUILD_SUCCESS` | Compiles and all tests pass | ✅ |
| `TEST_FAILURE` | Compiles, but tests fail | ❌ |
| `COMPILATION_FAILURE` | Still doesn't compile | ❌ |
| `ERROR_MODEL_RESPONSE` | AI call failed / unusable answer | ❌ |
 
**See every case:**
```bash
jq -r 'to_entries[] | "\(.key)  \(.value.attempts[0].failureCategory)"' $E/runs/p1/deepseek-deepseek-chat/result_repair_deepseek-deepseek-chat.json
```
 
**BSR (Build Success Rate)** = fixed cases ÷ 12:
```bash
jq '[.[] | .attempts[0].successful] | {fixed: map(select(.)) | length, total: length}' $E/runs/p1/deepseek-deepseek-chat/result_repair_deepseek-deepseek-chat.json
```
Swap `runs/p1` for another run folder to check that run.
 
**CEFR (error fix rate)** and the comparison with the paper are calculated in `derived/` (see `derived/derive.sh`).
 
---
 
## Rules (from M1)
 
- **Don't rerun cases just because they failed.** A failed fix is a result.
- **Don't change settings to "make it work".** If something has to change, add a row to `deviations.md`,
  commit it, **then** rerun.
- **One person per run.** Say in the chat before starting.
- **Never commit the real `.env` or an API key.** If a key leaks, tell the group so it can be deleted.
- Always `git pull` before you start and `git push` when you're done.
---
 
## Git tags
 
- `m1-frozen`: M1 decisions, committed before any run
- `results-v1`: final derived results and decision
## Result
 
_To be filled in after the analysis: BSR and CEFR for each run, the comparison with the paper, and the verdict for each RQ._
