import pandas as pd
import pickle
import sys

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

def preprocess_data():
	file = 'test_summary.txt' if test_data else 'all_summary.txt'
	df = read_data(file)
	df = remove_ignored_classes(df)
	df = remove_duplicates(df)
	return remove_rare_classes(df)

def cache_dump(obj, name):
	with open('cache/' + name, 'wb') as file:
		pickle.dump(obj, file)

def cache_load(name):
	with open('cache/' + name, 'rb') as file:
		return pickle.load(file)

if len(sys.argv) < 2:
	sys.stderr.write('Usage: main.py preprocess|classify')
	sys.exit(1)

for param in sys.argv[1:]:
	if param == 'preprocess':
		df = preprocess_data()
		cache_dump(df, 'df')
	elif param == 'data':
		test_data = False
	elif param == 'test':
		test_data = True
	elif param == 'classify':
		print 'classify: not implemented'
	elif param == 'print':
		if 'df' not in locals():
			df = cache_load('df')
		print df
	else:
		sys.stderr.write('Unrecognized option: ' + sys.argv[1])
		sys.exit(1)