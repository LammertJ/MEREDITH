#
# Copyright [May 5, 2024] [Jacqueline Lammert, Maximilian Tschochohei]
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# This function uses cosine similarity based on text embeddings model to 
# compare two strings for their semantic similarity
#

from vertexai.language_models import TextEmbeddingModel
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def cosine(
    user_recommendation: str,
    model_recommendation: str
) -> str:
    #Cosine similarity by patient and biomarker

    text_embedding_model = TextEmbeddingModel.from_pretrained("textembedding-gecko@latest")
    emb1 = np.array(text_embedding_model.get_embeddings([user_recommendation])[0].values)
    emb2 = np.array(text_embedding_model.get_embeddings([model_recommendation])[0].values)
    emb1 = emb1.reshape(1,-1)
    emb2 = emb2.reshape(1,-1)
    cosine = cosine_similarity(emb1,emb2)[0][0]
    return cosine
