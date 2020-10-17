<template>
  <v-app>
    <div fluid>
    <H3> Working Job Cards</H3>
    <Card></Card>
    <div v-for="item in data" :key="item.name">
      <v-card class="mb-4">
        <v-list-item three-line>
          <v-list-item-content>
            <div class="overline mb-4">{{ item.name }}</div>
            <v-list-item-title class="headline mb-1">
              {{ item.operation }}
            </v-list-item-title>
            <v-list-item-subtitle>
              QTY: {{ item.for_quantity }}
            </v-list-item-subtitle>
            <v-list-item-subtitle>
              Production Item: {{ item.production_item }}
            </v-list-item-subtitle>
            <v-list-item-subtitle>
              Satus: {{ item.status }}
            </v-list-item-subtitle>
          </v-list-item-content>

          <v-list-item-avatar tile size="80" color="grey"></v-list-item-avatar>
        </v-list-item>

        <v-card-actions>
          <!-- <v-spacer></v-spacer> -->
          <v-btn text color="primary" @click="open_card(item)"> open </v-btn>
        </v-card-actions>
      </v-card>
    </div>
    </div>
  </v-app>
</template>

<script>
import { evntBus } from "./bus";
import Card from "./Card.vue";

export default {
  data: function () {
    return {
      data: "",
    };
  },
  components: {
    Card,
  },

  methods: {
    get_data() {
      const vm = this;
      frappe.call({
        method: "csf_tz.csf_tz.page.jobcards.jobcards.get_job_cards",
        args: {},
        async: true,
        callback: function (r) {
          if (r.message) {
            vm.data = r.message;
          }
        },
      });
    },
    open_card(item) {
      evntBus.$emit("open_card",item);
    },
  },
  created: function () {
    this.get_data();
  },
};
</script>
<style>
.navbar-default {
  height: 40px;
}
div.navbar .container {
  padding-top: 2px;
}
</style>