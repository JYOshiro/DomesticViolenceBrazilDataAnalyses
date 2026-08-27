# Alcohol and Reporting Context Dashboard

Static capstone dashboard built from aggregated SINAN, Vigitel, Ambev, protection-reporting, calendar, and policy-event data.

## AWS deployment

Pushes to `main` deploy `dashboard/` to a private S3 bucket behind CloudFront. The workflow uses GitHub OIDC, so AWS access keys are not stored in GitHub.

One-time AWS bootstrap:

1. In IAM, create the GitHub OIDC provider with URL `https://token.actions.githubusercontent.com` and audience `sts.amazonaws.com` if it does not already exist.
2. Deploy `infra/github-oidc-role.yml` in CloudFormation, supplying that provider ARN. Copy its `DeployRoleArn` output.
3. In GitHub repository **Settings > Secrets and variables > Actions > Variables**, set `AWS_DEPLOY_ROLE_ARN` to that output and `AWS_REGION` to the intended deployment region.
4. Approve the `production` environment deployment if GitHub requests it. The workflow provisions and updates the S3/CloudFront site automatically.

The public URL is emitted in each workflow run after CloudFront deployment. A custom domain can be added later with Route 53 and an ACM certificate in `us-east-1`.

## Refreshing dashboard data

The live site uses the checked-in aggregate files in `dashboard/data/`; it does not publish the local DuckDB database. To refresh them locally, run `work/export_dashboard_data.py` against the project database. The exporter applies `work/create_capstone_dashboard_views.sql` first.

Section 3 uses aggregated conditional profiles keyed by year, cohort, region, breakdown dimension, and breakdown value. Selecting a bar shows filter-aware victim, probable-perpetrator, age, schooling, and relationship insights without publishing row-level SINAN records. Probable-perpetrator age is not available in the supplied SINAN schema and is therefore not estimated.

After a refresh, validate the breakdown/profile grain and categorical reconciliations with `node work/validate_breakdown_insights.js`.

## Vigitel comparability

The dashboard deliberately displays a gap for 2022 because no Vigitel collection occurred. It also displays the legacy current-drinking indicator as unavailable for 2024: the supplied 2024 data does not populate the prior 30-day source field, and the available past-12-month and frequency fields are not substituted as though they were comparable.
