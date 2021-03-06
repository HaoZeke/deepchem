"""
Script that trains graph-conv models on Tox21 dataset.
"""
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import numpy as np
np.random.seed(123)
import tensorflow as tf
tf.random.set_seed(123)
import deepchem as dc
from membrane_permeability_datasets import load_permeability

# Load Tox21 dataset
permeability_tasks, permeability_datasets, transformers = load_permeability(
    featurizer='GraphConv')
train_dataset, valid_dataset, test_dataset = permeability_datasets

metric = dc.metrics.Metric(dc.metrics.pearson_r2_score, np.mean)

n_atom_feat = 75
batch_size = 64

max_atoms_train = max([mol.get_num_atoms() for mol in train_dataset.X])
max_atoms_valid = max([mol.get_num_atoms() for mol in valid_dataset.X])
max_atoms_test = max([mol.get_num_atoms() for mol in test_dataset.X])
max_atoms = max([max_atoms_train, max_atoms_valid, max_atoms_test])

reshard_size = 512
transformer = dc.trans.DAGTransformer(max_atoms=max_atoms)
train_dataset.reshard(reshard_size)
train_dataset = transformer.transform(train_dataset)
valid_dataset.reshard(reshard_size)
valid_dataset = transformer.transform(valid_dataset)

model = dc.models.DAGModel(
    len(permeability_tasks),
    max_atoms=max_atoms,
    n_atom_feat=n_atom_feat,
    batch_size=batch_size,
    learning_rate=1e-3,
    use_queue=False,
    mode='regression')

# Fit trained model
model.fit(train_dataset, nb_epoch=50)
print("Evaluating model")
train_scores = model.evaluate(train_dataset, [metric], transformers)
valid_scores = model.evaluate(valid_dataset, [metric], transformers)

print("Train scores")
print(train_scores)

print("Validation scores")
print(valid_scores)
