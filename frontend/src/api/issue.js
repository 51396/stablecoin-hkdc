import api from './index'

// 地址管理相关 API
export const issueAPI = {
  getKpi() {
    return api.get(`/issuance/kpi`);
  },
  getTasks(){
    return api.get(`/issuance/tasks`);
  },
  createRequest(data){
    return api.post(`/issuance/requests`,data);
  },
  approve(request_id){
    return api.post(`/issuance/requests/${request_id}/approve`);
  },
  execute(request_id){
    return api.post(`/issuance/requests/${request_id}/execute`);
  },

}


export default issueAPI