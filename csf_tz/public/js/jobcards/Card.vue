<template>
  <div justify="center" v-if="Dialog">
    <v-dialog v-model="Dialog" max-width="1200px">
      <v-card>
        <v-card-title>
          <span class="headline indigo--text">{{
            cardData.operation.name
          }}</span>
          <v-spacer></v-spacer>
          <div
            class="stopwatch"
            style="
              font-weight: bold;
              margin: 0px 13px 0px 2px;
              color: #545454;
              font-size: 18px;
              display: inline-block;
              vertical-align: text-bottom;
            "
          >
            <span class="hours">{{ timer.hours }}</span>
            <span class="colon">:</span>
            <span class="minutes">{{ timer.minutes }}</span>
            <span class="colon">:</span>
            <span class="seconds">{{ timer.seconds }}</span>
          </div>
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

            <v-autocomplete
              dense
              auto-select-first
              outlined
              color="indigo"
              label="Employee"
              v-model="cardData.employee"
              :items="employees"
              item-text="name"
              background-color="white"
              no-data-text="Customer not found"
              hide-details
              :readonly="cardData.employee ? true : false"
              :filter="customFilter"
            >
              <template v-slot:item="data">
                <template>
                  <v-list-item-content>
                    <v-list-item-title
                      class="indigo--text subtitle-1"
                      v-html="data.item.name"
                    ></v-list-item-title>
                    <v-list-item-subtitle
                      v-html="`${data.item.employee_name}`"
                    ></v-list-item-subtitle>
                  </v-list-item-content>
                </template>
              </template>
            </v-autocomplete>
          </v-col>
        </v-row>
        <v-card-actions class="mx-3">
          <v-btn v-if="!start" @click="start_por" color="success" dark
            >Start</v-btn
          >
          <v-btn v-if="start" @click="pause_por" color="warning" dark
            >Pause</v-btn
          >
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
    timer: {
      hours: 0,
      minutes: 0,
      seconds: 0,
    },
  }),
  watch: {
    Dialog(value) {
      if (value) {
        this.get_employees();
      }
    },
  },
  methods: {
    close_dialog() {
      this.Dialog = false;
    },
    start_por() {
      if (!this.cardData.employee) {
        evntBus.$emit("show_messag", "Please set Employee");
      } else {
        this.start = true;
        let row = frappe.model.add_child(
          this.cardData,
          "Job Card Time Log",
          "time_logs"
        );
        row.from_time = frappe.datetime.now_datetime();
        row.job_started = 1;
        row.started_time = row.from_time;
        row.status = "Work In Progress";
        if (!frappe.flags.resume_job) {
          this.cardData.current_time = 0;
        }
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
        args: { company: this.cardData.company },
        async: false,
        callback: function (r) {
          if (r.message) {
            employees = r.message;
          }
        },
      });
      this.employees = employees;
    },
    customFilter(item, queryText, itemText) {
      const searchText = queryText.toLowerCase();
      const textOne = item.name.toLowerCase();
      const textTwo = item.employee_name.toLowerCase();

      return (
        textOne.indexOf(searchText) > -1 || textTwo.indexOf(searchText) > -1
      );
    },
    set_timer() {
      const vm = this;
      let currentIncrement = this.cardData.current_time || 0;
      if (this.cardData.started_time || this.cardData.current_time) {
        if (this.cardData.status == "On Hold") {
          updateStopwatch(currentIncrement);
          console.log("currentIncrement",currentIncrement)
        } else {
          console.log("else")
          currentIncrement += moment(frappe.datetime.now_datetime()).diff(
            moment(this.cardData.started_time),
            "seconds"
          );
          console.log("diff",currentIncrement)
          initialiseTimer();
        }

        function initialiseTimer() {
          const interval = setInterval(() => {
            var current = setCurrentIncrement();
            console.log("current",current)
            updateStopwatch(current);
          }, 1000);
        }

        function updateStopwatch(increment) {
          // console.log(increment)
          var hours = Math.floor(increment / 3600);
          var minutes = Math.floor((increment - hours * 3600) / 60);
          var seconds = increment - hours * 3600 - minutes * 60;

          vm.timer.hours =
            hours < 10 ? "0" + hours.toString() : hours.toString();
          vm.timer.minutes =
            minutes < 10 ? "0" + minutes.toString() : minutes.toString();
          vm.timer.seconds =
            seconds < 10 ? "0" + seconds.toString() : seconds.toString();
        }

        function setCurrentIncrement() {
          currentIncrement += 1;
          return currentIncrement;
        }
      }
    },
  },
  created: function () {
    evntBus.$on("open_card", (job_card) => {
      this.Dialog = true;
      this.cardData = job_card;
      this.timer = {
      hours: 0,
      minutes: 0,
      seconds: 0,
    },
      this.set_timer();
    });
  },
};
</script>

<style>
</style>