<template>
  <v-row justify="center">
    <v-dialog v-model="Dialog" max-width="900px">
      <v-card>
        <v-card-title>
          <span class="headline indigo--text">Job Card</span>
        </v-card-title>
        <v-card-text class="pa-0">
          <v-list-item three-line>
          <v-list-item-content>
            <div class="overline mb-4">{{ cardData.name }}</div>
            <v-list-item-title class="headline mb-1">
              {{ cardData.operation }}
            </v-list-item-title>
            <v-list-item-subtitle>
              QTY: {{ cardData.for_quantity }}
            </v-list-item-subtitle>
            <v-list-item-subtitle>
              Production Item: {{ cardData.production_item }}
            </v-list-item-subtitle>
            <v-list-item-subtitle>
              Satus: {{ cardData.status }}
            </v-list-item-subtitle>
          </v-list-item-content>
          <v-list-item-avatar tile size="80" color="grey"></v-list-item-avatar>
          </v-list-item>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="error" dark @click="close_dialog">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-row>
</template>

<script>
import { evntBus } from "./bus";
export default {
  data: () => ({
    Dialog: false,
    cardData: ""
  }),
  watch: {},
  methods: {
    close_dialog() {
      this.Dialog = false;
    },
    
  },
  created: function () {
    evntBus.$on("open_card", (item) => {
      this.Dialog = true;
      this.cardData = item;

    });
  },
};
</script>