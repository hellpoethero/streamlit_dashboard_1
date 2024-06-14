import pandas as pd

def load_full_data():         
    df = pd.read_csv("data/all.csv")
    # df.columns = [col.replace("\\\\PIDATA\VA1_U2_","") for col in df.columns]

    df['Time'] = df["Time"].astype("datetime64[ns]")
    return df

def load_prediction():
    df = pd.read_csv("data/act.csv")
    df['DateTime'] = df["DateTime"].astype("datetime64[ns]")

    df_pred = pd.read_csv("data/prediction.csv")
    df_pred['DateTime'] = df_pred["DateTime"].astype("datetime64[ns]")
    df_pred['DateTimePrediction'] = df_pred["DateTimePrediction"].astype("datetime64[ns]")

    return df, df_pred

def load_sootblow():
    df = pd.read_csv("data/thoi_bui.csv", header=0, index_col=0)
    df['datetime'] = pd.to_datetime(df['datetime']).dt.tz_localize(None)
    start = df[df['status']=='start']
    stop = df[df['status']=='stop']

    new_df = pd.merge(start, stop, on=['group','cycle_full_gr'])
    new_df.columns = ["group","start_datetime",	"start_date","start_time","cycle_full_gr","status_x","gr_status_x","finish_datetime","finish_date","finish_time","status_y","gr_status_y"]
    new_df['duration (minutes)'] = ((new_df['finish_datetime'] - new_df['start_datetime']).dt.total_seconds() / 60).astype('int')
    
    return new_df
