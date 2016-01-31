import pandas as pd
import sys
from sklearn.externals import joblib
from sklearn.grid_search import GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.cross_validation import train_test_split
from sklearn.metrics import recall_score

test_data = True
lucky_number = 42
score_measure = 'recall_weighted'
tune_parameters = {
	'n_estimators': [130, 140, 150, 160, 170, 180],
	'max_features': ['sqrt', 'log2'] }

def cache_dump(obj, name):
	joblib.dump(obj, 'cache/' + name)

def cache_load(name):
	return joblib.load('cache/' + name)

def read_data(file, sep):
	return pd.read_csv(
		file,
		sep = sep,
		na_values = ["nan"],
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
		'part_step_FoFc_std_max','part_step_FoFc_std_step', 'resolution_max_limit']
	return df.drop(ignored_columns, axis = 1)

def preprocess_data():
	file = 'test_summary.txt' if test_data else 'all_summary.txt'
	df = read_data(file, ';')
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

def search(df):
	classes = df['res_name'].as_matrix()
	df = df.drop('res_name', axis = 1)
	X_train, X_test, y_train, y_test = create_train_test(df, classes)
	rfc = create_random_forest_classifier()
	clf = GridSearchCV(
		estimator = rfc,
		param_grid = tune_parameters,
		scoring = score_measure)
	clf.fit(X_train, y_train)
	best_rfc = clf.best_estimator_
	print 'Best params: ', clf.best_params_
	y_true, y_pred = y_test, best_rfc.predict(X_test)
	print 'Score (' + score_measure + '): ', recall_score(y_true, y_pred, average='weighted')
	return best_rfc

def classify(df, es):
	file = 'test_data.txt'
	tdf = read_data(file, ',')
	tdf = tdf[list(set(tdf.columns).intersection(df.columns))]
	tdf = tdf.fillna(0)
	pred = es.predict(tdf)
	with open('result.txt', 'wb') as f:
		f.writelines(["%s\n" % p for p in pred])

if len(sys.argv) < 2:
	sys.stderr.write('Usage: main.py [test|data] preprocess search classify print')
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
	elif param == 'search':
		if 'df' not in locals():
			df = cache_load('df')
		es = search(df)
		cache_dump(es, 'es')
	elif param == 'classify':
		if 'df' not in locals():
			df = cache_load('df')
		if 'es' not in locals():
			es = cache_load('es')
		classify(df, es)
	elif param == 'print':
		if 'df' not in locals():
			df = cache_load('df')
		print df.shape
	else:
		sys.stderr.write('Unrecognized option: ' + param)
		sys.exit(1)