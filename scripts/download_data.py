import urllib.request
import os
import zipfile
import sys
from parse_dataset import parse_dataset
from download_gene_names import download_gene_names
from create_statistics import create_statistics
#sys.path.insert(0, './parse_data_scripts')

urls = {
	"dataset1": {
		"parse": False,
		"create_statistics": False,
	},
	"dataset2": {
		"url":"https://www.dropbox.com/sh/1v31yeu0zb4jcmm/AAAi5medvxa_kIbAEB7Edywua?dl=1&preview=LargeSets.zip",
		"parse": False,
		"create_statistics": False,
	},
	"dataset3":	{
		"url":"https://www.dropbox.com/s/0hqq2g2ipefy1u1/large_allSampleTypes.zip?dl=1",
		"parse": True,
		"create_statistics": True,
	},
	"dataset4":	{
		"url":"https://www.dropbox.com/s/l2bpf4lka8jxktg/LargeSet.zip?dl=1",
		"parse": True,
		"create_statistics": True,
	},
	"gene_names": {
		"download_gene_names": True
	}
}

if not os.path.exists("data"):
	os.makedirs("data")

for dataset, url in urls.items():
	path = "data/" + dataset
	if "url" in url:
		if not os.path.exists(path):
			print("download " + dataset)
			os.makedirs(path)
			urllib.request.urlretrieve(url["url"], path + "/download.zip")
			print("unzip " + dataset)
			with zipfile.ZipFile(path + "/download.zip","r") as zip_ref:
				zip_ref.extractall(path)
			os.remove(path + "/download.zip")
		else:
			print("skip already downloaded " + dataset)

	if not os.path.exists(path + "/subsets") and "parse" in url:
		if url["parse"]:
			print("parse " + dataset)
			parse_dataset(dataset)
		else:
			print("parser for " + dataset + " not implemented yet. Stay tuned!")
	else:
		print("already parsed " + dataset)

	if not os.path.exists(path + "/statistics") and "create_statistics" in url:
		if url["create_statistics"]:
			print("creating statistics for " + dataset)
			create_statistics(dataset)
		else:
			print("skipping statistics for " + dataset)
	else:
		print("already created statistics for " + dataset)

	if "download_gene_names" in url and url["download_gene_names"] and not os.path.exists(path):
		os.makedirs(path)
		download_gene_names(path)
		print("downloaded genes names")

	print("finished " + dataset)
