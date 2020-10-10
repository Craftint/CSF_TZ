<template>
  <v-app>
    <H3> Working Job Cards</H3>
    <div v-for="item in data" :key="item.name">
      <v-card class="mb-4" >
        <v-list-item three-line>
          <v-list-item-content>
            <div class="overline mb-4">{{ item.name }}</div>
            <v-list-item-title class="headline mb-1">
              {{ item.production_item }}
            </v-list-item-title>
            <v-list-item-subtitle>
              {{ item.operation }}
              </v-list-item-subtitle>
              <v-list-item-subtitle>
              {{ item.status }}
              </v-list-item-subtitle>
          </v-list-item-content>

          <v-list-item-avatar tile size="80" color="grey"></v-list-item-avatar>
        </v-list-item>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text> open </v-btn>
        </v-card-actions>
      </v-card>
    </div>
  </v-app>
</template>
<script>
export default {
  data: function () {
    return {
      data: "",
    };
  },
  components: {},

  methods: {
    check_opening_entry() {
      const vm = this;
      frappe.call({
        method: "csf_tz.csf_tz.page.jobcards.jobcards.get_job_cards",
        args: {},
        async: true,
        callback: function (r) {
          if (r.message) {
            console.log(r.message);
            vm.data = r.message;
          }
        },
      });
    },
  },
  created: function () {
    this.check_opening_entry();
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