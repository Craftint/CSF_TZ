<template>
  <v-app>
    <div fluid>
      <H3> Working Job Cards</H3>
      <Card></Card>
      <div v-for="item in data" :key="item.name">
        <div :class="set_status_color(item.status)">
          <v-card class="mb-4">
            <v-list-item three-line>
              <v-list-item-content>
                <div class="overline mb-4">{{ item.name }}</div>
                <v-list-item-title class="headline mb-1">
                  {{ item.operation.name }}
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
                <v-card-subtitle v-if="item.current_time">Current Time: {{ item.current_time/60 }}</v-card-subtitle>
              </v-list-item-content>

              <v-img
                max-height="150"
                max-width="250"
                :src="item.operation.image"
              ></v-img>
            </v-list-item>

            <v-card-actions>
              <!-- <v-spacer></v-spacer> -->
              <v-btn text color="primary" @click="open_card(item)">
                open
              </v-btn>
            </v-card-actions>
          </v-card>
        </div>
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
      evntBus.$emit("open_card", item);
    },
    set_status_color(status){
      if (status == "Open") {
        return "status-Open"
      }
      if (status == "Work In Progress") {
        return "status-Work"
      }
      if (status == "Material Transferred") {
        return "status-Material"
      }
      if (status == "On Hold") {
        return "status-Hold"
      }
      if (status == "Submitted") {
        return "status-Submitted"
      }
    }
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
.status-Open {
  border-left: 5px solid purple;
}
.status-Work {
  border-left: 5px solid lime;
}
.status-Material {
  border-left: 5px solid teal;
}
.status-Hold {
  border-left: 5px solid #607D8B;
}
.status-Submitted {
  border-left: 5px solid #FF5722;
}
</style>