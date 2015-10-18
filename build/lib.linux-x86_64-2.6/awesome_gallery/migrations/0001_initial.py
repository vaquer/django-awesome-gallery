# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Gallery'
        db.create_table(u'awesome_gallery_gallery', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=200)),
            ('about', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('administrator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('ugc', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('high_definition', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'awesome_gallery', ['Gallery'])

        # Adding M2M table for field tags on 'Gallery'
        m2m_table_name = db.shorten_name(u'awesome_gallery_gallery_tags')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('gallery', models.ForeignKey(orm[u'awesome_gallery.gallery'], null=False)),
            ('tag', models.ForeignKey(orm[u'app.tag'], null=False))
        ))
        db.create_unique(m2m_table_name, ['gallery_id', 'tag_id'])

        # Adding model 'Item'
        db.create_table(u'awesome_gallery_item', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=200)),
            ('short_description', self.gf('django.db.models.fields.TextField')()),
            ('url_video', self.gf('django.db.models.fields.URLField')(max_length=250)),
            ('image', self.gf('awesome_gallery.fields.ImageWithThumbsField')(max_length=100)),
            ('order', self.gf('django.db.models.fields.IntegerField')(db_index=True)),
            ('date', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('gallery', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='items', null=True, to=orm['awesome_gallery.Gallery'])),
            ('high_definition', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('vertical', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('display_title', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'awesome_gallery', ['Item'])

        # Adding M2M table for field tags on 'Item'
        m2m_table_name = db.shorten_name(u'awesome_gallery_item_tags')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('item', models.ForeignKey(orm[u'awesome_gallery.item'], null=False)),
            ('tag', models.ForeignKey(orm[u'app.tag'], null=False))
        ))
        db.create_unique(m2m_table_name, ['item_id', 'tag_id'])


    def backwards(self, orm):
        # Deleting model 'Gallery'
        db.delete_table(u'awesome_gallery_gallery')

        # Removing M2M table for field tags on 'Gallery'
        db.delete_table(db.shorten_name(u'awesome_gallery_gallery_tags'))

        # Deleting model 'Item'
        db.delete_table(u'awesome_gallery_item')

        # Removing M2M table for field tags on 'Item'
        db.delete_table(db.shorten_name(u'awesome_gallery_item_tags'))


    models = {
        u'app.tag': {
            'Meta': {'object_name': 'Tag'},
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '200', 'primary_key': 'True'})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'awesome_gallery.gallery': {
            'Meta': {'object_name': 'Gallery'},
            'about': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'administrator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'high_definition': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '200'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['app.Tag']", 'symmetrical': 'False'}),
            'ugc': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'awesome_gallery.item': {
            'Meta': {'object_name': 'Item'},
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'display_title': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'gallery': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'items'", 'null': 'True', 'to': u"orm['awesome_gallery.Gallery']"}),
            'high_definition': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('awesome_gallery.fields.ImageWithThumbsField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'order': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'short_description': ('django.db.models.fields.TextField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '200'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['app.Tag']", 'symmetrical': 'False'}),
            'url_video': ('django.db.models.fields.URLField', [], {'max_length': '250'}),
            'vertical': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['awesome_gallery']