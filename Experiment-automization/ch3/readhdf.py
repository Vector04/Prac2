import pandas

with pandas.HDFStore('test_results.h5') as hdf:
    print(hdf.keys())
# df = pd.read_hdf('test_results.h5', key='test_result')
# print(df)