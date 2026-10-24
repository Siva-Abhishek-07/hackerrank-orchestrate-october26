import pandas as pd

df_act = pd.read_csv('dataset/system_activity.csv')
retain_acts = df_act[df_act['event_type'] == 'RETAIN_RECORD']
print(f"Total RETAIN_RECORD activities: {len(retain_acts)}")
print(retain_acts.head(20)[['activity_id', 'event_time', 'source_system', 'target_system', 'resource_id', 'reported_result', 'details']])
