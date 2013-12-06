



class AnnotatorLibrary(object):

    _annotator_functors = {}

    @classmethod
    def register(cls, name, annotator_functor):
        assert not name in cls._annotator_functors
        cls._annotator_functors[name] = annotator_functor

    @classmethod
    def apply_annotator(cls, 

