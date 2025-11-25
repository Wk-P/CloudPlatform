from django.db import models


# --- Models aligned with frontend (DetectorView.vue) ---
class IngressBlacklistItem(models.Model):
	"""Ingress controller blacklist/control item.
	Fields are intentionally flexible to match frontend display keys.
	"""
	# One of source/ip/cidr/pattern may be used by UI
	source = models.CharField(max_length=256, blank=True, default="")
	ip = models.GenericIPAddressField(null=True, blank=True)
	cidr = models.CharField(max_length=64, blank=True, default="")
	pattern = models.CharField(max_length=256, blank=True, default="")

	# Control/Action fields
	action = models.CharField(max_length=64, blank=True, default="")
	mode = models.CharField(max_length=64, blank=True, default="")
	control = models.CharField(max_length=128, blank=True, default="")

	# Scope/Target
	scope = models.CharField(max_length=128, blank=True, default="")
	target = models.CharField(max_length=128, blank=True, default="")

	# Meta
	reason = models.CharField(max_length=256, blank=True, default="")
	note = models.CharField(max_length=256, blank=True, default="")
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		indexes = [
			models.Index(fields=["ip", "cidr", "pattern"]),
		]


class IngressTrafficSample(models.Model):
	"""Traffic trend data point for the Ingress controller.
	Store timestamp and a numeric value (e.g., RPS or QPS).
	"""
	ts = models.DateTimeField(db_index=True)
	value = models.FloatField()
	# optional label fields in case of multi-series expansion in future
	metric = models.CharField(max_length=64, blank=True, default="")  # e.g., rps
	scope = models.CharField(max_length=128, blank=True, default="")  # e.g., namespace/app

	class Meta:
		indexes = [models.Index(fields=["ts"])]

