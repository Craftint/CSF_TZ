<template>
  <div justify="center" v-if="Dialog">
    <v-dialog v-model="Dialog" max-width="1200px">
      <v-card>
        <v-card-title>
          <span class="headline indigo--text">{{
            cardData.operation.name
          }}</span>
          <v-spacer></v-spacer>
          <span class="overline">{{ cardData.name }}</span>
        </v-card-title>
        <v-row class="mx-3">
          <v-col cols="5">
            <v-img
              max-height="600"
              max-width="600"
              class="img-border"
              :src="
                cardData.operation.image ||
                '/assets/csf_tz/js/jobcards/placeholder-image.png'
              "
            >
            </v-img>
          </v-col>
          <v-col cols="4">
            <v-card-text class="pa-0">
              <v-list-item three-line>
                <v-list-item-content>
                  <v-textarea
                    label="Operation Description"
                    auto-grow
                    outlined
                    rows="3"
                    row-height="25"
                    readonly
                    v-model="cardData.operation.description"
                  >
                  </v-textarea>
                  <v-list-item-subtitle class="subtitle-1 mb-1">
                    QTY: {{ cardData.for_quantity }}
                  </v-list-item-subtitle>
                  <v-list-item-subtitle class="subtitle-1 mb-1">
                    Production Item: {{ cardData.production_item }}
                  </v-list-item-subtitle>
                  <v-list-item-subtitle class="subtitle-1 mb-1">
                    Satus: {{ cardData.status }}
                  </v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </v-card-text>
          </v-col>
          <v-col cols="3">
            <v-img
              max-height="400"
              max-width="400"
              class="img-border"
              :src="
                cardData.work_order_image ||
                '/assets/csf_tz/js/jobcards/placeholder-image.png'
              "
            >
            </v-img>
            <v-divider></v-divider>

          </v-col>
        </v-row>
        <v-card-actions class="mx-3">
          <v-btn v-if="!start" @click="start_por" color="success" dark >Start</v-btn>
          <v-btn v-if="start" @click="pause_por" color="warning" dark >Pause</v-btn>
          <v-btn color="primary" dark @click="close_dialog">Submit</v-btn>
          <v-spacer></v-spacer>
          <v-btn color="error" dark @click="close_dialog">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { evntBus } from "./bus";
export default {
  data: () => ({
    Dialog: false,
    cardData: "",
    start: false,
    employees: "",
  }),
  watch: {
    Dialog(value) {
      if (value) {
        this.get_employees()
      }
    },
  },
  methods: {
    close_dialog() {
      this.Dialog = false;
    },
    start_por() {
      if (!this.cardData.employee) {
          frappe.msgprint("Please set Employee")
      
      } else {
        this.start = true;
        console.log(this.get_employees())
      }
    },
    pause_por() {
      this.start = false;
    },
    get_employees() {
      const vm = this;
      let employees;
      frappe.call({
        method: "csf_tz.csf_tz.page.jobcards.jobcards.get_employees",
        args: {company:this.cardData.company},
        async: false,
        callback: function (r) {
          if (r.message) {
            employees = r.message;
          }
        },
      });
      this.employees = employees
    },
  },
  created: function () {
    evntBus.$on("open_card", (job_card) => {
      this.Dialog = true;
      this.cardData = job_card;
    });
  },
};
</script>

<style>
</style>