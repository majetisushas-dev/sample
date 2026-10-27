from ecsc_rag.core import normalize,em,f1,feat
def test_em(): assert em('The Eiffel Tower!',['Eiffel Tower'])==1
def test_f1(): assert f1('red blue',['blue green'])==.5
def test_shape(): assert feat('who','Ada','Ada wrote it').shape==(1,8)

