# Copyright 2009-2023 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class AccountCodaTransCode(models.Model):
    _name = "account.coda.trans.code"
    _description = "CODA transaction code"
    _order = "code"

    name = fields.Char(compute="_compute_name", readonly=True)
    code = fields.Char(size=2, required=True)
    type = fields.Selection(
        selection=[("code", "Transaction Code"), ("family", "Transaction Family")],
        required=True,
    )
    parent_id = fields.Many2one("account.coda.trans.code", string="Family")
    description = fields.Char(translate=True)
    comment = fields.Text(translate=True)

    @api.depends("code", "description", "type", "parent_id")
    def _compute_name(self):
        for rec in self:
            name = rec.code
            if rec.description:
                name += " " + rec.description
            if rec.type == "code":
                family = rec.parent_id.code
                name += " (" + _("Family %s") % family + ")"
            rec.name = len(name) > 55 and name[:55] + "..." or name

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search([("code", "like", name)] + args, limit=limit)
        if not recs:
            recs = self.search([("description", operator, name)] + args, limit=limit)
        return [(r.id, r.name) for r in recs]

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if not args:
            args = []
        new_args = []
        for arg in args:
            if len(arg) == 3 and arg[0] == "name":
                new_arg = [
                    "|",
                    ("code", arg[1], arg[2]),
                    ("description", arg[1], arg[2]),
                ]
                new_args += new_arg
            else:
                new_args.append(arg)
        return super().search(
            new_args, offset=offset, limit=limit, order=order, count=count
        )
