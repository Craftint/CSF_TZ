import Job_Cards from './JobCards.vue';

frappe.provide('frappe.JobCards');


frappe.JobCards.job_cards = class {
        constructor({ parent }) {
                this.$parent = $(parent);
                this.page = parent.page;
                this.make_body();
        }
        make_body() {
                this.$EL = this.$parent.find('.layout-main');
                this.vue = new Vue({
                        vuetify: new Vuetify(),
                        el: this.$EL[0],
                        data: {
                        },
                        render: h => h(Job_Cards),
                });
        }
        setup_header() {

        }
};