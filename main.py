import pandas as pd

test_data = True

def read_data(file):
	return pd.read_csv(
		file,
		sep=";",
		na_values=["nan"],
		keep_default_na = False)

def remove_ignored_classes(df):
	ignored_classes = {'DA','DC','DT', 'DU',
		'DG', 'DI','UNK', 'UNX',
		'UNL', 'PR', 'PD', 'Y1',
		'EU', 'N', '15P', 'UQ',
		'PX4'}
	return df[~df.res_name.isin(ignored_classes) & ~df.res_name.isnull()]

def remove_duplicates(df):
	return df.drop_duplicates(subset = ['res_name', 'pdb_code'])

def remove_rare_classes(df):
	class_sizes = df.groupby(['res_name']).size()
	rare_classes = set(class_sizes[class_sizes < 5].index)
	return df[~df.res_name.isin(rare_classes)]

def preprocess_data(df):
	df = remove_ignored_classes(df)
	df = remove_duplicates(df)
	return remove_rare_classes(df)

file = 'test_summary.txt' if test_data else 'all_summary.txt'
df = read_data(file)

if test_data:
	print 'test print: '
	print df
	print

df = preprocess_data(df)

print df