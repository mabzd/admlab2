import pandas as pd

test_data = True

if test_data:
	data_file = "test_summary.txt"
else:
	data_file = "all_summary.txt"

df = pd.read_csv(
	data_file,
	sep=";",
	na_values=["nan"],
	keep_default_na = False)

if test_data:
	print 'test print: '
	print df
	print

# remove ignored and null classes
def remove_ignored_classes(df):
	ignored_classes = {'DA','DC','DT', 'DU',
		'DG', 'DI','UNK', 'UNX',
		'UNL', 'PR', 'PD', 'Y1',
		'EU', 'N', '15P', 'UQ',
		'PX4'}
	return df[~df.res_name.isin(ignored_classes) & ~df.res_name.isnull()]

# remove duplicated rows
def remove_duplicates(df):
	return df.drop_duplicates(subset = ['res_name', 'pdb_code'])

# remove rare instances (less than 5 examples)
def remove_rare_classes(df):
	class_sizes = df.groupby(['res_name']).size()
	rare_classes = set(class_sizes[class_sizes < 5].index)
	return df[~df.res_name.isin(rare_classes)]

df = remove_ignored_classes(df)
df = remove_duplicates(df)
df = remove_rare_classes(df)

print df