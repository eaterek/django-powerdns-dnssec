"""Models and signal subscriptions for templating system"""

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from powerdns.models.powerdns import Domain, Record


class DomainTemplate(models.Model):
    """A predefined template containing several record templates"""
    name = models.CharField(_('Name'), unique=True, max_length=255)


class RecordTemplate(models.Model):
    """A predefined record template that would cause a corresponding record
    to be created."""
    domain_template = models.ForeignKey(
        DomainTemplate, verbose_name=_('Domain template')
    )
    type = models.CharField(
        _("type"), max_length=6, blank=True, null=True,
        choices=Record.RECORD_TYPE, help_text=_("Record type"),
    )
    name = models.CharField(_('name'), max_length=255)
    content = models.CharField(_('content'), max_length=255)
    ttl = models.PositiveIntegerField(
        _("TTL"), blank=True, null=True, default=3600,
        help_text=_("TTL in seconds"),
    )
    prio = models.PositiveIntegerField(
        _("priority"), blank=True, null=True,
        help_text=_("For MX records, this should be the priority of the"
                    " mail exchanger specified"),
    )
    auth = models.NullBooleanField(
        _("authoritative"),
        help_text=_("Should be set for data for which is itself"
                    " authoritative, which includes the SOA record and our own"
                    " NS records but not set for NS records which are used for"
                    " delegation or any delegation related glue (A, AAAA)"
                    " records"),
        default=True,
    )
    remarks = models.TextField(_('Additional remarks'), blank=True)

    def create_record(self, domain):
        """Creates, saves and returns a record for this domain"""
        kwargs = {}
        template_kwargs = {
            'domain-name': domain.name,
        }
        for argname in ['type', 'ttl', 'prio', 'auth']:
            kwargs[argname] = getattr(self, argname)
        for argname in ['name', 'content']:
            kwargs[argname] = getattr(self, argname).format(**template_kwargs)
        kwargs['template'] = self
        kwargs['domain'] = domain
        record = Record.objects.create(**kwargs)
        return record


@receiver(
    post_save, sender=Domain, dispatch_uid='domain_update_templated_records'
)
def update_templated_records(sender, instance, **kwargs):
    """Deletes and creates records appropriately to the template"""
    if instance.template is None:
        return
    instance.record_set.exclude(
        template__isnull=True
    ).exclude(
        template__domain_template=instance.template
    ).delete()
    existing_template_ids = set(
        instance.record_set.exclude(
            template__isnull=True
        ).values_list('template__id', flat=True)
    )
    for template in instance.template.recordtemplate_set.exclude(
        pk__in=existing_template_ids,
    ):
        template.create_record(instance)