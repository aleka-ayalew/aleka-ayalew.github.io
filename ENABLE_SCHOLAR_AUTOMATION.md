chore: instructions for enabling Google Scholar automation

This branch adds a GitHub Actions workflow and a scraper to fetch Google Scholar citation and publication counts and commit them to data/citations.json. To enable and run the workflow, follow these steps:

1. Add repository secret SCHOLAR_URL with your Google Scholar profile URL:
   - Go to Settings → Secrets and variables → Actions → New repository secret
   - Name: SCHOLAR_URL
   - Value: https://scholar.google.com/citations?hl=en&user=Yda5OkEAAAAJ

2. Merge this branch into the default branch (main). After merging, the workflow will be available on the main branch.

3. Trigger the workflow manually (optional):
   - Go to Actions → Update Google Scholar citations → Run workflow → choose branch main → Run

4. After a successful run, confirm data/citations.json appears in the repository root and that your site now displays the updated counts.
