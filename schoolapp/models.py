from django.db import models


class Classes(models.Model):
    number = models.IntegerField()
    letter = models.CharField(max_length=1)
    isactive = models.BooleanField(default=True)
    teacher = models.ForeignKey('Teachers', on_delete=models.SET_NULL, blank=True, null=True)
    createdon = models.DateTimeField(auto_now_add=True)
    modifiedon = models.DateTimeField(auto_now=True)
    createdby = models.CharField(max_length=128)
    modifiedby = models.CharField(max_length=128, blank=True)
    isdeleted = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.number}-{self.letter}'

    class Meta:
        db_table = 'Classes'
        verbose_name = 'Classes'
        verbose_name_plural = 'Classes'


class Gender(models.Model):
    type = models.CharField(max_length=128)
    createdon = models.DateTimeField(auto_now_add=True)
    modifiedon = models.DateTimeField(auto_now=True)
    createdby = models.CharField(max_length=128)
    modifiedby = models.CharField(max_length=128, blank=True)
    isdeleted = models.BooleanField(default=False)

    def __str__(self):
        return self.type

    # def clean(self):
    #     if self.pk and not self.modifiedby:
    #         raise ValidationError({'modifiedby': 'This field is required.'})

    class Meta:
        db_table = 'Gender'
        verbose_name = 'Gender'
        verbose_name_plural = 'Gender'


class Payment(models.Model):
    type = models.CharField(max_length=128)
    createdon = models.DateTimeField(auto_now_add=True)
    modifiedon = models.DateTimeField(auto_now=True)
    createdby = models.CharField(max_length=128)
    modifiedby = models.CharField(max_length=128, blank=True)
    isdeleted = models.BooleanField(default=False)

    def __str__(self):
        return self.type

    # def clean(self):
    #     if self.pk and not self.modifiedby:
    #         raise ValidationError({'modifiedby': 'This field is required.'})

    class Meta:
        db_table = 'Payment'
        verbose_name = 'Payment'
        verbose_name_plural = 'Payment'


class Parents(models.Model):
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    surname = models.CharField(max_length=128, blank=True)
    phone = models.CharField(max_length=20)
    createdon = models.DateTimeField(auto_now_add=True)
    modifiedon = models.DateTimeField(auto_now=True)
    createdby = models.CharField(max_length=128)
    modifiedby = models.CharField(max_length=128, blank=True)
    isdeleted = models.BooleanField()
    note = models.TextField(blank=True)

    def __str__(self):
        return ' '.join(filter(None, [self.first_name, self.last_name, self.surname]))

    # def clean(self):
    #     if self.pk and not self.modifiedby:
    #         raise ValidationError({'modifiedby': 'This field is required.'})

    class Meta:
        db_table = 'Parents'
        verbose_name = 'Parents'
        verbose_name_plural = 'Parents'


class Pupils(models.Model):
    GENDER_CHOICES = [
        ('Мальчик', 'Мальчик'),
        ('Девочка', 'Девочка'),
    ]
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    surname = models.CharField(max_length=128, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    birthday = models.DateField()
    classes = models.ForeignKey('Classes', on_delete=models.SET_NULL, null=True)
    createdon = models.DateTimeField(auto_now_add=True)
    modifiedon = models.DateTimeField(auto_now=True)
    createdby = models.CharField(max_length=128)
    modifiedby = models.CharField(max_length=128, blank=True)
    isdeleted = models.BooleanField(default=False)
    note = models.TextField(blank=True)

    def __str__(self):
        return ' '.join(filter(None, [self.first_name, self.last_name, self.surname]))

    # def clean(self):
    #     if self.pk and not self.modifiedby:
    #         raise ValidationError({'modifiedby': 'This field is required.'})

    class Meta:
        db_table = 'Pupils'
        verbose_name = 'Pupils'
        verbose_name_plural = 'Pupils'


class ParentPupil(models.Model):
    parent = models.ForeignKey(Parents, on_delete=models.CASCADE, null=True, verbose_name='Parent')
    pupil = models.ForeignKey(Pupils, on_delete=models.CASCADE, null=True, verbose_name='Child')

    def __str__(self):
        return (f'Parent: {self.parent}'
                f'Child: {self.pupil}')

    class Meta:
        unique_together = ('parent', 'pupil')
        db_table = 'ParentsAndPupils'
        verbose_name = 'Parents And Pupils'
        verbose_name_plural = 'Parents And Pupils'


class Teachers(models.Model):
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    surname = models.CharField(max_length=128, blank=True)
    createdon = models.DateTimeField(auto_now_add=True)
    modifiedon = models.DateTimeField(auto_now=True)
    createdby = models.CharField(max_length=128)
    modifiedby = models.CharField(max_length=128, blank=True)
    isdeleted = models.BooleanField(max_length=128)

    def __str__(self):
        return ' '.join(filter(None, [self.first_name, self.last_name, self.surname]))

    # def clean(self):
    #     if self.pk and not self.modifiedby:
    #         raise ValidationError({'modifiedby': 'This field is required.'})

    class Meta:
        db_table = 'Teachers'
        verbose_name = 'Teachers'
        verbose_name_plural = 'Teachers'
