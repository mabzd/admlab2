import pandas as pd
import pickle
import sys
from sklearn.grid_search import GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.cross_validation import train_test_split

test_data = True
lucky_number = 42
score_measure = 'recall_weighted'
tune_parameters = {
	'n_estimators': [50, 100, 150],
	'max_features': ['sqrt', 'log2'] }

def cache_dump(obj, name):
	with open('cache/' + name, 'wb') as file:
		pickle.dump(obj, file)

def cache_load(name):
	with open('cache/' + name, 'rb') as file:
		return pickle.load(file)

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

def remove_ignored_columns(df):
	ignored_columns = ['title', 'pdb_code', 'res_id', 'chain_id',
		'local_BAa', 'local_NPa', 'local_Ra', 'local_RGa',
		'local_SRGa', 'local_CCSa', 'local_CCPa', 'local_ZOa',
		'local_ZDa', 'local_ZD_minus_a', 'local_ZD_plus_a', 'local_res_atom_count',
		'local_res_atom_non_h_count', 'local_res_atom_non_h_occupancy_sum',
		'local_res_atom_non_h_electron_sum', 'local_res_atom_non_h_electron_occupancy_sum',
		'local_res_atom_C_count', 'local_res_atom_N_count', 'local_res_atom_O_count',
		'local_res_atom_S_count', 'dict_atom_non_h_count', 'dict_atom_non_h_electron_sum',
		'dict_atom_C_count', 'dict_atom_N_count', 'dict_atom_O_count', 'dict_atom_S_count',
		'fo_col', 'fc_col', 'weight_col', 'grid_space',
		'solvent_radius', 'solvent_opening_radius', 'part_step_FoFc_std_min',
		'part_step_FoFc_std_max','part_step_FoFc_std_step']
	return df.drop(ignored_columns, axis = 1)

def preprocess_data():
	file = 'test_summary.txt' if test_data else 'all_summary.txt'
	df = read_data(file)
	df = remove_ignored_classes(df)
	df = remove_duplicates(df)
	df = remove_rare_classes(df)
	df = remove_ignored_columns(df)
	df = df.fillna(0)
	return df

def create_random_forest_classifier():
	return RandomForestClassifier(
		n_jobs = -1,
		n_estimators = 50,
		oob_score = True,
		random_state = lucky_number)

def create_train_test(df, classes):
	return train_test_split(
		df,
		classes,
		test_size = 0.2,
		random_state = lucky_number,
		stratify = classes)

def tune(df):
	classes = df['res_name'].as_matrix()
	df = df.drop('res_name', axis = 1)
	X_train, X_test, y_train, y_test = create_train_test(df, classes)
	estimator = create_random_forest_classifier()
	clf = GridSearchCV(
		estimator = estimator,
		param_grid = tune_parameters,
		scoring = score_measure)
	clf.fit(X_train, y_train)
	print clf.best_params_
	return clf.best_estimator_

def classify(df):
	classes = df['res_name'].as_matrix()
	df = df.drop('res_name', axis = 1)
	print df

if len(sys.argv) < 2:
	sys.stderr.write('Usage: main.py [test|data] preprocess tune classify print')
	sys.exit(1)

for param in sys.argv[1:]:
	print 'Executing: ' + param + '...'
	if param == 'preprocess':
		df = preprocess_data()
		cache_dump(df, 'df')
	elif param == 'data':
		test_data = False
		print 'Using real data'
	elif param == 'test':
		test_data = True
		print 'Using test data'
	elif param == 'tune':
		if 'df' not in locals():
			df = cache_load('df')
		es = tune(df)
		cache_dump(es, 'es')
	elif param == 'classify':
		if 'df' not in locals():
			df = cache_load('df')
		classify(df)
	elif param == 'print':
		if 'df' not in locals():
			df = cache_load('df')
		print df
	else:
		sys.stderr.write('Unrecognized option: ' + sys.argv[1])
		sys.exit(1)