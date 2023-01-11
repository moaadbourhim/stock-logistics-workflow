# Copyright 2015-2016 Agile Business Group (<http://www.agilebg.com>)
# Copyright 2016 BREMSKERL-REIBBELAGWERKE EMMERLING GmbH & Co. KG
#    Author Marco Dieckhoff
# Copyright 2018 Alex Comba - Agile Business Group
# Copyright 2023 Simone Rubino - TAKOBI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from odoo.fields import first
from .stock_move_line import check_date


class StockMove(models.Model):
    _inherit = "stock.move"

    def _backdating_action_done(self, moves_todo):
        """Process the moves one by one, backdating the ones that need to."""
        for move in self:
            move_line = first(move.move_line_ids)
            date_backdating = move_line.date_backdating
            if date_backdating:
                move = move.with_context(
                    date_backdating=date_backdating,
                )

            moves_todo |= super(StockMove, move)._action_done()

            # overwrite date field where applicable
            date_backdating = move_line.date_backdating
            if date_backdating:
                check_date(date_backdating)
                move.date = date_backdating
                move.move_line_ids.update({
                    'date': date_backdating,
                })
        return moves_todo

    @api.multi
    def _action_done(self):
        moves_todo = self.env['stock.move']
        has_move_lines_to_backdate = any(self.mapped('move_line_ids.date_backdating'))
        if not has_move_lines_to_backdate:
            moves_todo |= super()._action_done()
        else:
            moves_todo = self._backdating_action_done(moves_todo)
        return moves_todo
