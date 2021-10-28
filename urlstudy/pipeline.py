from analyzer.pipeline import FilePipeline
# from analyzer import DB_URI, DB_NAME, DB_COLLECTION_NAME

my_pipeline = FilePipeline()

my_pipeline.add_stage('ReadabilityStage')
my_pipeline.add_stage('RemoveTagsExceptLinksStage')
my_pipeline.add_stage('SentenceTokenizationStage')
my_pipeline.add_stage('NationalCountryCollectionStage')
my_pipeline.add_stage('NytThemeTagsStage')
my_pipeline.add_stage('StudyWeekIndexStage')
my_pipeline.add_stage('SentenceLinkStage')
