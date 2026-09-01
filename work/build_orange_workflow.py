import base64
import pickle
from pathlib import Path

from orangewidget.utils.filedialogs import RecentPath


PROJECT_DIR = Path(__file__).resolve().parent.parent
ORANGE_DIR = PROJECT_DIR / "orange"
OUTPUT = ORANGE_DIR / "daily_notification_prediction.ows"
TRAIN = ORANGE_DIR / "prediction_train_pre_2023.tab"
TEST = ORANGE_DIR / "prediction_test_2023_2025.tab"


def file_properties(path):
    payload = {
        "controlAreaVisible": True,
        "recent_paths": [RecentPath(str(path.resolve()), None, None)],
        "recent_urls": [],
        "sheet_names": {},
        "source": 0,
        "url": "",
        "__version__": 3,
    }
    return base64.b64encode(pickle.dumps(payload, protocol=4)).decode("ascii")


def main():
    if not TRAIN.exists() or not TEST.exists():
        raise FileNotFoundError("Run build_prediction_story.py with Orange before creating the workflow.")

    train_props = file_properties(TRAIN)
    test_props = file_properties(TEST)
    workflow = f"""<?xml version='1.0' encoding='utf-8'?>
<scheme version="2.0" title="Daily notification prediction" description="Orange-reproducible chronological evaluation: train before 2023 and test from 2023 onward.">
  <nodes>
    <node id="0" name="File" qualified_name="Orange.widgets.data.owfile.OWFile" project_name="Orange3" version="" title="Training data: before 2023" position="(80.0, 145.0)" />
    <node id="1" name="File" qualified_name="Orange.widgets.data.owfile.OWFile" project_name="Orange3" version="" title="Test data: 2023-2025" position="(80.0, 335.0)" />
    <node id="2" name="Tree" qualified_name="Orange.widgets.model.owtree.OWTreeLearner" project_name="Orange3" version="" title="Regression Tree" position="(330.0, 105.0)" />
    <node id="3" name="Random Forest" qualified_name="Orange.widgets.model.owrandomforest.OWRandomForest" project_name="Orange3" version="" title="Random Forest" position="(330.0, 210.0)" />
    <node id="4" name="Test and Score" qualified_name="Orange.widgets.evaluate.owtestandscore.OWTestAndScore" project_name="Orange3" version="" title="Test on 2023-2025 data" position="(590.0, 205.0)" />
    <node id="5" name="Predictions" qualified_name="Orange.widgets.evaluate.owpredictions.OWPredictions" project_name="Orange3" version="" title="Holdout predictions" position="(590.0, 375.0)" />
    <node id="6" name="Feature Importance" qualified_name="orangecontrib.explain.widgets.owpermutationimportance.OWPermutationImportance" project_name="Orange3-Explain" version="" title="Tree feature importance" position="(830.0, 95.0)" />
    <node id="7" name="Feature Importance" qualified_name="orangecontrib.explain.widgets.owpermutationimportance.OWPermutationImportance" project_name="Orange3-Explain" version="" title="Forest feature importance" position="(830.0, 245.0)" />
    <node id="8" name="Data Table" qualified_name="Orange.widgets.data.owtable.OWTable" project_name="Orange3" version="" title="Prediction rows" position="(830.0, 405.0)" />
  </nodes>
  <links>
    <link id="0" source_node_id="0" sink_node_id="4" source_channel="Data" sink_channel="Data" enabled="true" source_channel_id="data" sink_channel_id="train_data" />
    <link id="1" source_node_id="1" sink_node_id="4" source_channel="Data" sink_channel="Test Data" enabled="true" source_channel_id="data" sink_channel_id="test_data" />
    <link id="2" source_node_id="2" sink_node_id="4" source_channel="Learner" sink_channel="Learner" enabled="true" source_channel_id="learner" sink_channel_id="learner" />
    <link id="3" source_node_id="3" sink_node_id="4" source_channel="Learner" sink_channel="Learner" enabled="true" source_channel_id="learner" sink_channel_id="learner" />
    <link id="4" source_node_id="0" sink_node_id="2" source_channel="Data" sink_channel="Data" enabled="true" source_channel_id="data" sink_channel_id="data" />
    <link id="5" source_node_id="0" sink_node_id="3" source_channel="Data" sink_channel="Data" enabled="true" source_channel_id="data" sink_channel_id="data" />
    <link id="6" source_node_id="1" sink_node_id="5" source_channel="Data" sink_channel="Data" enabled="true" source_channel_id="data" sink_channel_id="data" />
    <link id="7" source_node_id="2" sink_node_id="5" source_channel="Model" sink_channel="Predictors" enabled="true" source_channel_id="model" sink_channel_id="predictors" />
    <link id="8" source_node_id="3" sink_node_id="5" source_channel="Model" sink_channel="Predictors" enabled="true" source_channel_id="model" sink_channel_id="predictors" />
    <link id="9" source_node_id="1" sink_node_id="6" source_channel="Data" sink_channel="Data" enabled="true" source_channel_id="data" sink_channel_id="data" />
    <link id="10" source_node_id="2" sink_node_id="6" source_channel="Model" sink_channel="Model" enabled="true" source_channel_id="model" sink_channel_id="model" />
    <link id="11" source_node_id="1" sink_node_id="7" source_channel="Data" sink_channel="Data" enabled="true" source_channel_id="data" sink_channel_id="data" />
    <link id="12" source_node_id="3" sink_node_id="7" source_channel="Model" sink_channel="Model" enabled="true" source_channel_id="model" sink_channel_id="model" />
    <link id="13" source_node_id="5" sink_node_id="8" source_channel="Predictions" sink_channel="Data" enabled="true" source_channel_id="predictions" sink_channel_id="data" />
  </links>
  <annotations>
    <text id="0" type="text/plain" rect="(38.0, 30.0, 250.0, 56.0)" font-family="Helvetica" font-size="14">Pre-2023 observations train both regression models.</text>
    <text id="1" type="text/plain" rect="(38.0, 420.0, 270.0, 72.0)" font-family="Helvetica" font-size="14">The 2023-2025 file is separate test data. Do not randomly resample or cross-validate across this boundary.</text>
  </annotations>
  <thumbnail />
  <node_properties>
    <properties node_id="0" format="pickle">{train_props}</properties>
    <properties node_id="1" format="pickle">{test_props}</properties>
    <properties node_id="2" format="literal">{{'auto_apply': True, 'binary_trees': True, 'controlAreaVisible': True, 'learner_name': 'Regression Tree', 'limit_depth': True, 'max_depth': 8, 'limit_min_internal': True, 'min_internal': 20, 'limit_min_leaf': True, 'min_leaf': 10, 'limit_majority': False, 'sufficient_majority': 95, '__version__': 2}}</properties>
    <properties node_id="3" format="literal">{{'auto_apply': True, 'class_weight': False, 'controlAreaVisible': True, 'index_output': 0, 'learner_name': 'Random Forest', 'max_depth': 3, 'max_features': 8, 'min_samples_split': 5, 'n_estimators': 500, 'use_max_depth': False, 'use_max_features': True, 'use_min_samples_split': True, 'use_random_state': True, '__version__': 1}}</properties>
    <properties node_id="4" format="literal">{{'controlAreaVisible': True, 'resampling': 5, 'n_folds': 10, 'cv_stratified': False, 'n_repeats': 3, 'sample_size': 66, 'shuffle_stratified': False, 'use_rope': False, 'rope': 0.1, 'comparison_criterion': 0, '__version__': 4}}</properties>
  </node_properties>
  <session_state><window_groups /></session_state>
</scheme>
"""
    OUTPUT.write_text(workflow, encoding="utf-8")
    print(f"Created {OUTPUT}")


if __name__ == "__main__":
    main()
