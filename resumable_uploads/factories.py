import factory


class ResumableFileFactory(factory.django.DjangoModelFactory):
    path = factory.Faker('file_name')

    class Meta:
        model = 'resumable_uploads.ResumableFile'
