# -*- coding: utf-8 -*-
##############################################################################
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'MercadoLibre Financial Extension / Mercado Libre Publisher Extension',
    'summary': 'MercadoLibre Financial Extension / Mercado Libre Publisher Extension',
    'version': '15.0.23.2',
    'author': 'Moldeo Interactive',
    'website': 'https://www.moldeointeractive.com',
    "category": "Sales",
    "depends": ['base','meli_oerp'],
    'data': [
        'views/company_view.xml',
        #'views/configuration_view.xml',
        'views/financial_view.xml',
    ],
    'demo': [
    ],
    'price': '200.00',
    'currency': 'EUR',
    'images': [ 'static/description/main_screenshot.png',
                'static/description/meli_oerp_financial_configuration.png',
                'static/description/meli_oerp_financial_installation.png',
                'static/description/moldeo_interactive_logo.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'GPL-3',
}
