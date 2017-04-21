#!/usr/bin/python
""" Classes and functions for fitting the mean spherical diffusion kurtosis
model """
from __future__ import division, print_function, absolute_import

import numpy as np

from dipy.core.gradients import (check_multi_b, unique_bvals)
from dipy.reconst.base import ReconstModel
from dipy.reconst.dti import (MIN_POSITIVE_SIGNAL, iter_fit_tensor)


def mdki_prediction(dti_params, gtab, S0):
    """
    Predict a signal given the mean dki parameters.

    Parameters
    ----------


    Notes
    -----
    The predicted signal is given by: $MS(b) = S_0 * e^{-b ADC}$
    """
    prediction = 0
    return prediction


class MeanDiffusionKurtosisModel(ReconstModel):
    """ Mean spherical Diffusion Kurtosis Model
    """

    def __init__(self, gtab, bmag=None, return_S0_hat=False, *args, **kwargs):
        """ Mean Spherical Diffusion Kurtosis Model [1]_.

        Parameters
        ----------
        gtab : GradientTable class instance

        bmag : int
            The order of magnitude that the bvalues have to differ to be
            considered an unique b-value. Default: derive this value from the
            maximal b-value provided: $bmag=log_{10}(max(bvals)) - 1$.

        return_S0_hat : bool
            Boolean to return (True) or not (False) the S0 values for the fit.

        args, kwargs : arguments and key-word arguments passed to the
           fit_method. See mdti.wls_fit_mdki for details

        min_signal : float
            The minimum signal value. Needs to be a strictly positive
            number. Default: minimal signal in the data provided to `fit`.

        References
        ----------
        .. [1] Henriques, R.N., Correia, M.M., 2017. Interpreting age-related
               changes based on the mean signal diffusion kurtosis. 25th Annual
               Meeting of the ISMRM; Honolulu. April 22-28
        """
        ReconstModel.__init__(self, gtab)

        self.ubvals = unique_bvals(gtab.bvals, bmag)
        self.return_S0_hat = return_S0_hat
        self.design_matrix = design_matrix(self.ubvals)
        self.args = args
        self.kwargs = kwargs
        self.min_signal = self.kwargs.pop('min_signal', None)
        if self.min_signal is not None and self.min_signal <= 0:
            e_s = "The `min_signal` key-word argument needs to be strictly"
            e_s += " positive."
            raise ValueError(e_s)

        # Check if at least three b-values are given
        enough_b = check_multi_b(self.gtab, 3, non_zero=False)
        if not enough_b:
            mes = "MDKI requires at least 3 b-values (which can include b=0)"
            raise ValueError(mes)

    def fit(self, data, mask=None):
        """ Fit method of the DTI model class

        Parameters
        ----------
        data : array
            The measured signal from one voxel.

        mask : array
            A boolean array used to mark the coordinates in the data that
            should be analyzed that has the shape data.shape[:-1]

        """
        S0_params = None

        if mask is not None:
            # Check for valid shape of the mask
            if mask.shape != data.shape[:-1]:
                raise ValueError("Mask is not the same shape as data.")
            mask = np.array(mask, dtype=bool, copy=False)
        data_in_mask = np.reshape(data[mask], (-1, data.shape[-1]))

        if self.min_signal is None:
            min_signal = MIN_POSITIVE_SIGNAL
        else:
            min_signal = self.min_signal

        data_in_mask = np.maximum(data_in_mask, min_signal)

        params_in_mask = wls_fit_mdki(self.design_matrix, data_in_mask,
                                      return_S0_hat=self.return_S0_hat,
                                      *self.args, **self.kwargs)
        if self.return_S0_hat:
            params_in_mask, model_S0 = params_in_mask

        if mask is None:
            out_shape = data.shape[:-1] + (-1, )
            params = params_in_mask.reshape(out_shape)
            if self.return_S0_hat:
                S0_params = model_S0.reshape(out_shape[:-1])
        else:
            params = np.zeros(data.shape[:-1] + (12,))
            params[mask, :] = params_in_mask
            if self.return_S0_hat:
                S0_params = np.zeros(data.shape[:-1] + (1,))
                S0_params[mask] = model_S0

        return MeanDiffusionKurtosisFit(self, params, model_S0=S0_params)

    def predict(self, dti_params, S0=1.):
        """
        Predict a signal for this TensorModel class instance given parameters.

        Parameters
        ----------
        params : ndarray
            The parameters of the mean spherical diffusion kurtosis model
        S0 : float or ndarray
            The non diffusion-weighted signal in every voxel, or across all
            voxels. Default: 1
        """
        return mdki_prediction(dti_params, self.gtab, S0)


class MeanDiffusionKurtosisFit(object):

    def __init__(self, model, model_params, model_S0=None):
        """ Initialize a MeanDiffusionKurtosisFit class instance.
        """
        self.model = model
        self.model_params = model_params
        self.model_S0 = model_S0

    def __getitem__(self, index):
        model_params = self.model_params
        model_S0 = self.model_S0
        N = model_params.ndim
        if type(index) is not tuple:
            index = (index,)
        elif len(index) >= model_params.ndim:
            raise IndexError("IndexError: invalid index")
        index = index + (slice(None),) * (N - len(index))
        if model_S0 is not None:
            model_S0 = model_S0[index[:-1]]
        return type(self)(self.model, model_params[index], model_S0=model_S0)

    @property
    def S0_hat(self):
        return self.model_S0

    @property
    def md(self):
        r"""
        Spherical Mean diffusitivity (MD) calculated from the mean spherical
        Diffusion Kurtosis Model.

        Returns
        ---------
        md : ndarray
            Calculated Spherical Mean diffusitivity.

        References
        ----------
        .. [1] Henriques, R.N., Correia, M.M., 2017. Interpreting age-related
               changes based on the mean signal diffusion kurtosis. 25th Annual
               Meeting of the ISMRM; Honolulu. April 22-28
        """
        return model_params[..., 0]
    
    @property
    def mk(self):
        r"""
        Spherical Mean Kurtosis (MK) calculated from the mean spherical
        Diffusion Kurtosis Model.

        Returns
        ---------
        mk : ndarray
            Calculated Spherical Mean diffusitivity.

        References
        ----------
        .. [1] Henriques, R.N., Correia, M.M., 2017. Interpreting age-related
               changes based on the mean signal diffusion kurtosis. 25th Annual
               Meeting of the ISMRM; Honolulu. April 22-28
        """
        return model_params[..., 1]

    def predict(self, gtab, S0=None, step=None):
        r"""
        Given a mean spherical diffusion kurtosis model fit, predict the signal
        on the vertices of a sphere

        Parameters
        ----------
        gtab : a GradientTable class instance
            This encodes the directions for which a prediction is made

        S0 : float array
           The mean non-diffusion weighted signal in each voxel. Default:
           The fitted S0 value in all voxels if it was fitted. Otherwise 1 in
           all voxels.

        step : int
            The chunk size as a number of voxels. Optional parameter with
            default value 10,000.

            In order to increase speed of processing, tensor fitting is done
            simultaneously over many voxels. This parameter sets the number of
            voxels that will be fit at once in each iteration. A larger step
            value should speed things up, but it will also take up more memory.
            It is advisable to keep an eye on memory consumption as this value
            is increased.

        Notes
        -----
        """
        predict = 0

        return predict


@iter_fit_tensor()
def _wls_fit_mdki(design_matrix, msignal, ng, return_S0_hat=False):
    r"""
    Helper function that fits the mean spherical diffusion kurtosis imaging
    based on a weighted least square solution [1]_.

    Parameters
    ----------
    design_matrix : array (nub, 3)
        Design matrix holding the covariants used to solve for the regression
        coefficients of the mean spherical diffusion kurtosis model. Note that
        nub is the number of unique b-values
    msignal : ndarray ([X, Y, Z, ..., nub])
        Mean signal along all gradient direction for each unique b-value
        Note that the last dimension should contain the signal means and nub
        is the number of unique b-values.
    ng : ndarray([X, Y, Z, ..., nub])
        Number of gradient directions used to compute the mean signal for
        all unique b-values
    return_S0_hat : bool
        Boolean to return (True) or not (False) the S0 values for the fit.

    Returns
    -------
    params : array (..., 2)
        Containing the mean spherical diffusivity and mean spherical kurtosis

    References
    ----------
    .. [1] Henriques, R.N., Correia, M.M., 2017. Interpreting age-related
           changes based on the mean signal diffusion kurtosis. 25th Annual
           Meeting of the ISMRM; Honolulu. April 22-28
    """
    # Define weights as diag(sqrt(ng) * msignal ** 2)
    W = np.diag(ng * msignal ** 2)

    # WLS solution
    BTW = np.dot(design_matrix.T, W)
    inv_BT_W_B = np.linalg.pinv(np.dot(BTW, design_matrix))
    invBTWB_BTW = np.dot(inv_BT_W_B, BTW)
    params = np.dot(invBTWB_BTW, np.log(msignal))

    # Convert 2nd parameter to MK
    params[1] = params[1] / (params[0]**2)

    if return_S0_hat:
        return (params[:2], np.exp(params[2]))
    else:
        return params[:2]


def design_matrix(ubvals):
    """  Constructs design matrix for the mean spherical diffusion kurtosis
    model

    Parameters
    ----------
    ubals : Unique b-values

    dtype : string
        Parameter to control the dtype of returned designed matrix

    Returns
    -------
    design_matrix : array (nb, 3)
        Design matrix or B matrix for the mean spherical diffusion kurtosis
        model assuming that parameters are in the following order:
        design_matrix[j, :] = (MD, MK, S0)
    """
    nb = ubvals.shape
    B = np.zeros(nb + (3,))
    B[:, 0] = -ubvals
    B[:, 1] = 1.0/6.0 * ubvals**2
    B[:, 2] = np.ones(nb)
    return B
