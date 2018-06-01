from os.path import join
import codecs
import json
from global_.embedding import EmbeddingModel
from utils.cache import LMDBClient
from utils import data_utils
from utils import feature_utils
from utils import settings

global_dir = join(settings.DATA_DIR, 'global')


def pubs_load_generator():
    pubs_fname = 'pubs_features_raw.txt'
    with codecs.open(join(global_dir, pubs_fname), 'r', encoding='utf-8') as rf:
        for line in rf:
            yield json.loads(line)


def dump_author_features_lmdb():
    emb_model = EmbeddingModel.load('scopus')
    cnt = 0
    idf = data_utils.load_data(global_dir, 'feature_idf.pkl')
    LMDB_NAME = "author_100.emb.weighted"
    lc = LMDBClient(LMDB_NAME)
    for paper in pubs_load_generator():
        if not "title" in paper or not "authors" in paper:
            continue
        if len(paper["authors"]) > 30:
            print(cnt, paper["sid"], len(paper["authors"]))
        if len(paper["authors"]) > 100:
            continue
        if cnt % 1000 == 0:
            print(cnt, paper["sid"], len(paper["authors"]))
        cnt += 1
        author_features = feature_utils.extract_author_features(paper)
        for i, f in enumerate(author_features):
            lc.set("%s-%s" % (paper["sid"], i), emb_model.project_embedding(f, idf))


if __name__ == '__main__':
    dump_author_features_lmdb()
