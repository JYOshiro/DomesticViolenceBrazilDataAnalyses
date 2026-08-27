const fs = require('fs');
const path = require('path');

const projectDir = path.resolve(__dirname, '..');
const dataPath = path.join(projectDir, 'dashboard', 'data', 'dashboard-data.json');
const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));

function key(row) {
  return [
    row.year,
    row.cohort_code,
    row.region_name,
    row.dimension_name,
    row.dimension_value
  ].join('|');
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

assert(Array.isArray(data.breakdownInsights), 'breakdownInsights dataset is missing');
assert(data.breakdownInsights.length > 0, 'breakdownInsights dataset is empty');

const breakdownCounts = new Map(data.breakdowns.map(row => [key(row), Number(row.notification_count)]));
const seen = new Set();
const schoolingFields = [
  'schooling_none_count',
  'schooling_grades_1_4_incomplete_count',
  'schooling_grade_4_complete_count',
  'schooling_grades_5_8_incomplete_count',
  'schooling_primary_complete_count',
  'schooling_secondary_incomplete_count',
  'schooling_secondary_complete_count',
  'schooling_higher_incomplete_count',
  'schooling_higher_complete_count',
  'schooling_not_applicable_count',
  'schooling_unknown_count'
];

data.breakdownInsights.forEach(row => {
  const rowKey = key(row);
  const count = Number(row.notification_count);
  assert(!seen.has(rowKey), `Duplicate insight grain: ${rowKey}`);
  seen.add(rowKey);
  assert(breakdownCounts.has(rowKey), `Insight has no matching breakdown: ${rowKey}`);
  assert(breakdownCounts.get(rowKey) === count, `Notification count mismatch: ${rowKey}`);

  const victimSexTotal = Number(row.victim_sex_female_count)
    + Number(row.victim_sex_male_count)
    + Number(row.victim_sex_unknown_count);
  assert(victimSexTotal === count, `Victim-sex counts do not reconcile: ${rowKey}`);

  const perpetratorSexTotal = Number(row.perpetrator_sex_male_count)
    + Number(row.perpetrator_sex_female_count)
    + Number(row.perpetrator_sex_both_count)
    + Number(row.perpetrator_sex_unknown_count);
  assert(perpetratorSexTotal === count, `Perpetrator-sex counts do not reconcile: ${rowKey}`);
  assert(Number(row.victim_age_known_count) <= count, `Valid-age count exceeds notifications: ${rowKey}`);
  const schoolingTotal = schoolingFields.reduce((total, field) => total + Number(row[field]), 0);
  assert(schoolingTotal === count, `Schooling counts do not reconcile: ${rowKey}`);
  if (Number(row.victim_age_known_count)) {
    const meanAge = Number(row.victim_age_sum) / Number(row.victim_age_known_count);
    assert(meanAge >= 0 && meanAge <= 120, `Mean victim age is outside the valid range: ${rowKey}`);
  }
});

assert(seen.size === breakdownCounts.size, 'Breakdown and insight grains differ');
console.log(`Validated ${seen.size} breakdown insight rows with zero reconciliation errors.`);
