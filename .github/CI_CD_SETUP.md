# GitHub Actions CI/CD Setup

This project uses GitHub Actions for automated ETL pipeline execution, validation, and deployment.

## Workflows

### 1. ETL Scheduled Run (`etl_scheduled.yml`)
- **Trigger**: Daily at 2 AM UTC (configurable via cron)
- **Trigger Alternative**: Manual dispatch via Actions tab
- **Steps**:
  1. Checks out latest code
  2. Sets up Python 3.10 environment
  3. Installs dependencies from `requirements.txt`
  4. Runs `src/etl_pipeline.py` to clean and process raw data
  5. Runs `src/load_to_sqlite.py` to update SQLite database
  6. Commits updated processed CSVs and `supply_chain.db` to main
  7. Pushes changes back to GitHub

**Configuration**: Edit the cron schedule in `.github/workflows/etl_scheduled.yml`:
```yaml
schedule:
  - cron: "0 2 * * *"  # Daily at 2 AM UTC
```

Common cron patterns:
- `"0 2 * * *"` — Daily at 2 AM UTC
- `"0 2 * * 0"` — Weekly on Sunday at 2 AM UTC
- `"0 */6 * * *"` — Every 6 hours

### 2. ETL Validation (`etl_validation.yml`)
- **Trigger**: On every push to main and pull requests
- **Steps**:
  1. Lint Python code with flake8
  2. Validate ETL functions (dedup logic, type conversions)
  3. Check raw data files exist
  4. Verify processed outputs are in place

**Purpose**: Catch issues early before merging or deploying.

### 3. Streamlit Dashboard Deploy (`deploy_streamlit.yml`)
- **Trigger**: On push to main when `dashboard/app.py` or data changes
- **Steps**:
  1. Validates Streamlit app structure
  2. Posts deployment comment on PRs with instructions
  3. Confirms dashboard is ready for deployment

**Manual Deploy to Streamlit Cloud**:
```bash
streamlit cloud deploy --logger.level=debug
```

## Setting Up Secrets (if needed)

If your ETL needs credentials (DB connection, API keys, etc.), add them as GitHub Secrets:
1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add your secret (e.g., `DB_PASSWORD`)
4. Reference in workflow: `${{ secrets.DB_PASSWORD }}`

Example in `etl_scheduled.yml`:
```yaml
- name: Run ETL with credentials
  env:
    DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
  run: python3 src/etl_pipeline.py
```

## Data Push Permissions

The ETL scheduled run commits and pushes results back to main. This requires:
1. **Branch protection rules**: Allow GitHub Actions to push (Settings → Branches)
2. **Token permissions**: Workflow uses default `GITHUB_TOKEN` (sufficient for this repo)

If issues arise, create a Personal Access Token:
1. Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Create token with `repo` scope
3. Add as secret `GH_TOKEN`
4. Update workflow: `token: ${{ secrets.GH_TOKEN }}`

## Manual Trigger

Manually run workflows from GitHub UI:
1. Go to **Actions** tab
2. Select workflow (e.g., "ETL Pipeline - Scheduled Run")
3. Click **Run workflow** → **Run workflow**

## Monitoring & Logs

- **View logs**: Actions tab → workflow run → job logs
- **Status badge**: Add to README:
  ```markdown
  ![ETL Scheduled](https://github.com/YOUR_OWNER/ETL-Based-Supply-Chain-Data-Integration-Pipeline/actions/workflows/etl_scheduled.yml/badge.svg)
  ![ETL Validation](https://github.com/YOUR_OWNER/ETL-Based-Supply-Chain-Data-Integration-Pipeline/actions/workflows/etl_validation.yml/badge.svg)
  ```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Permission denied" on push | Ensure GitHub token has repo access and branch doesn't have strict push rules |
| Workflow not triggering | Check trigger conditions (cron, branches, filters) in YAML |
| Python package install fails | Update `requirements.txt`; check for platform-specific packages (e.g., psycopg2 may need dev tools) |
| Database locked error | Ensure only one ETL runs at a time; add concurrency controls if needed |

## Advanced: Notifications

Add Slack/Email notifications on job completion:

```yaml
- name: Notify Slack
  if: failure()
  uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {
        "text": "ETL pipeline failed: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

---

For more info: [GitHub Actions Documentation](https://docs.github.com/en/actions)
