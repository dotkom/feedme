# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Restaurant'
        db.create_table(u'feedme_restaurant', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('restaurant_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('menu_url', self.gf('django.db.models.fields.URLField')(max_length=250)),
            ('phone_number', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('buddy_system', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'feedme', ['Restaurant'])

        # Adding model 'Order'
        db.create_table(u'feedme_order', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('restaurant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['feedme.Restaurant'])),
        ))
        db.send_create_signal(u'feedme', ['Order'])

        # Adding model 'OrderLine'
        db.create_table(u'feedme_orderline', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['feedme.Order'])),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'owner', to=orm['auth.User'])),
            ('menu_item', self.gf('django.db.models.fields.IntegerField')(max_length=2)),
            ('soda', self.gf('django.db.models.fields.CharField')(max_length=25, null=True, blank=True)),
            ('extras', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('price', self.gf('django.db.models.fields.IntegerField')(default=100, max_length=4)),
        ))
        db.send_create_signal(u'feedme', ['OrderLine'])

        # Adding M2M table for field users on 'OrderLine'
        m2m_table_name = db.shorten_name(u'feedme_orderline_users')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('orderline', models.ForeignKey(orm[u'feedme.orderline'], null=False)),
            ('user', models.ForeignKey(orm[u'auth.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['orderline_id', 'user_id'])

        # Adding model 'Balance'
        db.create_table(u'feedme_balance', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('balance', self.gf('django.db.models.fields.FloatField')(default=0)),
        ))
        db.send_create_signal(u'feedme', ['Balance'])

        # Adding model 'ManageBalance'
        db.create_table(u'feedme_managebalance', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['feedme.Balance'])),
            ('deposit', self.gf('django.db.models.fields.FloatField')(default=0)),
        ))
        db.send_create_signal(u'feedme', ['ManageBalance'])

        # Adding model 'ManageOrders'
        db.create_table(u'feedme_manageorders', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('orders', self.gf('django.db.models.fields.related.OneToOneField')(related_name=u'Orders', unique=True, to=orm['feedme.Order'])),
        ))
        db.send_create_signal(u'feedme', ['ManageOrders'])

        # Adding model 'ManageUsers'
        db.create_table(u'feedme_manageusers', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'feedme', ['ManageUsers'])

        # Adding M2M table for field users on 'ManageUsers'
        m2m_table_name = db.shorten_name(u'feedme_manageusers_users')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('manageusers', models.ForeignKey(orm[u'feedme.manageusers'], null=False)),
            ('user', models.ForeignKey(orm[u'auth.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['manageusers_id', 'user_id'])

        # Adding model 'ManageOrderLimit'
        db.create_table(u'feedme_manageorderlimit', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order_limit', self.gf('django.db.models.fields.IntegerField')(default=100)),
        ))
        db.send_create_signal(u'feedme', ['ManageOrderLimit'])


    def backwards(self, orm):
        # Deleting model 'Restaurant'
        db.delete_table(u'feedme_restaurant')

        # Deleting model 'Order'
        db.delete_table(u'feedme_order')

        # Deleting model 'OrderLine'
        db.delete_table(u'feedme_orderline')

        # Removing M2M table for field users on 'OrderLine'
        db.delete_table(db.shorten_name(u'feedme_orderline_users'))

        # Deleting model 'Balance'
        db.delete_table(u'feedme_balance')

        # Deleting model 'ManageBalance'
        db.delete_table(u'feedme_managebalance')

        # Deleting model 'ManageOrders'
        db.delete_table(u'feedme_manageorders')

        # Deleting model 'ManageUsers'
        db.delete_table(u'feedme_manageusers')

        # Removing M2M table for field users on 'ManageUsers'
        db.delete_table(db.shorten_name(u'feedme_manageusers_users'))

        # Deleting model 'ManageOrderLimit'
        db.delete_table(u'feedme_manageorderlimit')


    models = {
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
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'feedme.balance': {
            'Meta': {'object_name': 'Balance'},
            'balance': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        },
        u'feedme.managebalance': {
            'Meta': {'object_name': 'ManageBalance'},
            'deposit': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['feedme.Balance']"})
        },
        u'feedme.manageorderlimit': {
            'Meta': {'object_name': 'ManageOrderLimit'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order_limit': ('django.db.models.fields.IntegerField', [], {'default': '100'})
        },
        u'feedme.manageorders': {
            'Meta': {'object_name': 'ManageOrders'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'orders': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "u'Orders'", 'unique': 'True', 'to': u"orm['feedme.Order']"})
        },
        u'feedme.manageusers': {
            'Meta': {'object_name': 'ManageUsers'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'Users'", 'symmetrical': 'False', 'to': u"orm['auth.User']"})
        },
        u'feedme.order': {
            'Meta': {'object_name': 'Order'},
            'date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'restaurant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['feedme.Restaurant']"})
        },
        u'feedme.orderline': {
            'Meta': {'object_name': 'OrderLine'},
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'owner'", 'to': u"orm['auth.User']"}),
            'extras': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'menu_item': ('django.db.models.fields.IntegerField', [], {'max_length': '2'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['feedme.Order']"}),
            'price': ('django.db.models.fields.IntegerField', [], {'default': '100', 'max_length': '4'}),
            'soda': ('django.db.models.fields.CharField', [], {'max_length': '25', 'null': 'True', 'blank': 'True'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'buddies'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['auth.User']"})
        },
        u'feedme.restaurant': {
            'Meta': {'object_name': 'Restaurant'},
            'buddy_system': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'menu_url': ('django.db.models.fields.URLField', [], {'max_length': '250'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'restaurant_name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['feedme']